import asyncio
import os
import requests
import random
import threading
import json
import shutil
import tkinter.messagebox as messagebox
import customtkinter as ctk
from dotenv import load_dotenv
from camoufox.async_api import AsyncCamoufox
from browserforge.fingerprints import Screen
from platformdirs import user_cache_dir,user_data_dir
load_dotenv()

SERPAPI = os.getenv("SERPAPI_KEY")

PROFILES_DIR = "bing_profiles"
if not os.path.exists(PROFILES_DIR):
    os.makedirs(PROFILES_DIR)


# --- CUSTOM DIALOG FOR PROFILE CREATION ---
class CreateProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save, on_cancel):
        super().__init__(parent)
        self.title("Add New Account")
        self.geometry("320x350")
        self.resizable(False, False)
        self.grab_set()

        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        ctk.CTkLabel(self, text="Create New Profile", font=("Arial", 18, "bold")).pack(pady=(20, 10))

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Profile Name (e.g., manhkiller1)", width=250)
        self.name_entry.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Microsoft Email", width=250)
        self.email_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.pass_entry.pack(pady=10)

        self.btn_save = ctk.CTkButton(self, text="Save Account", command=self.save)
        self.btn_save.pack(pady=(20, 10))

    def save(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.pass_entry.get()

        if name and email and password:
            self.on_save_callback(name, email, password)
            self.destroy()

    def cancel(self):
        self.on_cancel_callback()
        self.destroy()


# --- MAIN APP ---
class BingChillingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bing Rewards Automator")
        self.geometry("450x600")

        self.loop = asyncio.new_event_loop()
        self.browser_thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.browser_thread.start()

        self.page = None
        self.shutdown_event = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- UI SETUP ---
        self.title_label = ctk.CTkLabel(self, text="BING CHILLING", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(20, 10))

        self.profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.profile_frame.pack(pady=10)

        existing_profiles = self.get_existing_profiles()
        combo_values = ["-- Create New Profile --"] + existing_profiles

        self.profile_combo = ctk.CTkComboBox(
            self.profile_frame,
            values=combo_values,
            width=180,
            command=self.on_profile_select,
            state="readonly"
        )
        self.profile_combo.pack(side="left", padx=(0, 5))

        self.btn_rename = ctk.CTkButton(self.profile_frame, text="Rename", width=60, command=self.rename_profile)
        self.btn_rename.pack(side="left", padx=(0, 5))

        self.btn_delete = ctk.CTkButton(self.profile_frame, text="Delete", width=60, fg_color="#C62828",
                                        hover_color="#8E0000", command=self.delete_profile)
        self.btn_delete.pack(side="left")

        if existing_profiles:
            self.profile_combo.set(existing_profiles[0])
        else:
            self.profile_combo.set("-- Create New Profile --")

        self.btn_login = ctk.CTkButton(self, text="1. Start Browser & Login", command=self.run_login)
        self.btn_login.pack(pady=(10, 20))

        self.btn_run_all = ctk.CTkButton(self, text="▶ Run All Tasks sequentially", fg_color="green",
                                         hover_color="darkgreen", command=self.run_all_tasks)
        self.btn_daily_quest = ctk.CTkButton(self, text="Do Daily Quests", command=self.run_daily_quest)
        self.btn_daily_search = ctk.CTkButton(self, text="Do Daily Searches", command=self.run_daily_search)
        self.btn_search_trend = ctk.CTkButton(self, text="Do Search Trends", command=self.run_search_trend)

        self.status_label = ctk.CTkLabel(self, text="Ready to start.", text_color="gray")
        self.status_label.pack(pady=(15, 0))

        self.btn_quit = ctk.CTkButton(self, text="Quit Application", fg_color="#C62828", hover_color="#8E0000",
                                      command=self.on_closing)
        self.btn_quit.pack(side="bottom", pady=20)

    # --- PROFILE MANAGEMENT ---
    def check_install(self):
        cache_dir = user_cache_dir("camoufox","camoufox")
        if os.path.exists(cache_dir):
            try:
                if len(os.listdir(cache_dir)) >0 :
                    return True
            except Exception:
                pass
        return False
    def get_existing_profiles(self):
        return [d for d in os.listdir(PROFILES_DIR) if os.path.isdir(os.path.join(PROFILES_DIR, d))]

    def refresh_profile_list(self, select_name=None):
        profiles = self.get_existing_profiles()
        self.profile_combo.configure(values=["-- Create New Profile --"] + profiles)
        if select_name and select_name in profiles:
            self.profile_combo.set(select_name)
        elif profiles:
            self.profile_combo.set(profiles[0])
        else:
            self.profile_combo.set("-- Create New Profile --")

    def on_profile_select(self, choice):
        if choice == "-- Create New Profile --":
            dialog = CreateProfileDialog(self, self.save_new_profile, self.cancel_new_profile)

    def save_new_profile(self, name, email, password):
        profile_path = os.path.join(PROFILES_DIR, name)
        os.makedirs(profile_path, exist_ok=True)

        cred_path = os.path.join(profile_path, "credentials.json")
        with open(cred_path, "w") as f:
            json.dump({"email": email, "password": password}, f)

        self.refresh_profile_list(select_name=name)
        self.update_status(f"Account '{name}' saved successfully!")

    def cancel_new_profile(self):
        self.refresh_profile_list()

    def rename_profile(self):
        current_name = self.profile_combo.get()
        if current_name == "-- Create New Profile --" or not current_name:
            return

        dialog = ctk.CTkInputDialog(text=f"Rename '{current_name}' to:", title="Rename Profile")
        new_name = dialog.get_input()

        if new_name:
            new_name = new_name.strip()
            old_path = os.path.join(PROFILES_DIR, current_name)
            new_path = os.path.join(PROFILES_DIR, new_name)

            if os.path.exists(old_path) and not os.path.exists(new_path):
                os.rename(old_path, new_path)
                self.refresh_profile_list(select_name=new_name)
                self.update_status(f"Renamed profile to: {new_name}")
            else:
                self.update_status("Error: Name already exists.")

    def delete_profile(self):
        current_name = self.profile_combo.get()
        if current_name == "-- Create New Profile --" or not current_name:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete the profile '{current_name}'?\n\nThis will remove all saved cookies and login credentials."
        )

        if confirm:
            profile_path = os.path.join(PROFILES_DIR, current_name)
            try:
                shutil.rmtree(profile_path)
                self.refresh_profile_list()
                self.update_status(f"Deleted profile: {current_name}")
            except Exception as e:
                self.update_status(f"Error deleting profile: {e}")

    # --- UI RESET & STATE HELPERS ---
    def reset_ui(self):
        """Restores the UI to the initial state when the browser is closed."""
        self.page = None
        self.profile_combo.configure(state="readonly")
        self.btn_rename.configure(state="normal")
        self.btn_delete.configure(state="normal")
        self.btn_login.configure(state="normal", text="1. Start Browser & Login")

        # Hide all the task buttons again
        self.btn_run_all.pack_forget()
        self.btn_daily_quest.pack_forget()
        self.btn_daily_search.pack_forget()
        self.btn_search_trend.pack_forget()

    def show_task_buttons(self):
        self.profile_combo.configure(state="disabled")
        self.btn_rename.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        self.btn_login.configure(state="disabled", text="Browser Active")
        self.btn_run_all.pack(pady=5)
        self.btn_daily_quest.pack(pady=5)
        self.btn_daily_search.pack(pady=5)
        self.btn_search_trend.pack(pady=5)

    def disable_trend_btn(self):
        self.after(0, lambda: self.btn_search_trend.configure(state="disabled", text="Trends Completed (3/3)"))

    def set_task_buttons_state(self, state):
        self.btn_run_all.configure(state=state)
        self.btn_daily_quest.configure(state=state)
        self.btn_daily_search.configure(state=state)
        if state == "normal" and "Completed" not in self.btn_search_trend.cget("text"):
            self.btn_search_trend.configure(state=state)
        elif state == "disabled":
            self.btn_search_trend.configure(state=state)

    # --- THREADING & LIFECYCLE ---
    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_closing(self):
        self.update_status("Shutting down cleanly...")
        if self.shutdown_event:
            self.loop.call_soon_threadsafe(self.shutdown_event.set)
        self.destroy()

    def update_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text))

    async def browser_session(self, needs_download=False):
        profile_name = self.profile_combo.get().strip()
        if profile_name == "-- Create New Profile --":
            self.update_status("Please select or create a profile first!")
            self.btn_login.configure(state="normal")
            return

        profile_path = os.path.join(PROFILES_DIR, profile_name)

        if needs_download:
            self.update_status("Downloading... do not close the app")
        else:
            self.update_status(f"Opening browser using '{profile_name}'...")

        constrains = Screen(max_width=1280, max_height=720)
        try:
            async with AsyncCamoufox(
                    screen=constrains,
                    headless=False,
                    humanize=2.0,
                    persistent_context=True,
                    user_data_dir=profile_path
            ) as browser:
                if needs_download:
                    self.update_status("Download complete! Opening browser...")

                pages = browser.pages
                self.page = pages[0] if pages else await browser.new_page()

                # --- 1. LISTEN FOR BROWSER CLOSE ---
                browser_closed_event = asyncio.Event()

                def on_close(page_instance):
                    self.loop.call_soon_threadsafe(browser_closed_event.set)

                self.page.on("close", on_close)

                await self.execute_login(profile_name)

                self.after(0, self.show_task_buttons)
                self.update_status("Login verified. Ready for tasks.")

                self.shutdown_event = asyncio.Event()

                # --- Wait for EITHER the app to close, or the browser to be closed manually ---
                shutdown_task = asyncio.create_task(self.shutdown_event.wait())
                browser_close_task = asyncio.create_task(browser_closed_event.wait())

                await asyncio.wait(
                    [shutdown_task, browser_close_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                if browser_closed_event.is_set():
                    self.update_status("Browser was closed by user.")
                else:
                    self.update_status("Browser closed.")

        except Exception as e:
            if "closed" in str(e).lower() or "target" in str(e).lower():
                self.update_status("Browser was closed before finishing.")
            else:
                self.update_status(f"Browser Error: {e}")
        finally:
            # --- 3. RESET UI ---
            self.after(0, self.reset_ui)

    # --- BUTTON COMMANDS (Dispatchers) ---
    def run_login(self):
        needs_download = False
        if not self.check_install():
            confirm = messagebox.askyesno(
                "Camoufox is required to run"
                "The required stealth browser engine (~300MB) is not installed on this PC.\n\nWould you like to download it now? (This happens automatically but may take a few minutes)."
            )
            if not confirm:
                return
            needs_download = True
        self.btn_login.configure(state="disabled")
        asyncio.run_coroutine_threadsafe(self.browser_session(), self.loop)

    def run_all_tasks(self):
        asyncio.run_coroutine_threadsafe(self.run_task_safely(self.task_all_sequential), self.loop)

    def run_daily_quest(self):
        asyncio.run_coroutine_threadsafe(self.run_task_safely(self.task_daily_quest), self.loop)

    def run_daily_search(self):
        asyncio.run_coroutine_threadsafe(self.run_task_safely(self.task_daily_search), self.loop)

    def run_search_trend(self):
        asyncio.run_coroutine_threadsafe(self.run_task_safely(self.task_search_trend), self.loop)

    async def run_task_safely(self, task_coroutine):
        # --- Guardrail: Prevent task from running if browser is already dead ---
        if not self.page or self.page.is_closed():
            self.update_status("Cannot run task: Browser is closed!")
            return

        self.after(0, lambda: self.set_task_buttons_state("disabled"))
        try:
            await task_coroutine()
            self.update_status("Task complete. Ready.")
        except Exception as e:
            # --- 2. CATCH TASKS CRASHING DUE TO BROWSER CLOSE ---
            if "closed" in str(e).lower() or "target" in str(e).lower():
                self.update_status("Task cancelled: Browser was closed.")
            else:
                self.update_status(f"Task error: {e}")
        finally:
            # Only re-enable buttons if the browser is still alive
            if self.page and not self.page.is_closed():
                self.after(0, lambda: self.set_task_buttons_state("normal"))

    # --- AUTOMATION LOGIC ---
    async def task_all_sequential(self):
        self.update_status("Running ALL tasks sequentially...")
        await self.task_daily_quest()
        await self.task_daily_search()
        await self.task_search_trend()
        self.update_status("All tasks sequentially finished!")

    async def execute_login(self, profile_name):
        cred_path = os.path.join(PROFILES_DIR, profile_name, "credentials.json")
        acc_email = ""
        acc_password = ""

        if os.path.exists(cred_path):
            with open(cred_path, "r") as f:
                creds = json.load(f)
                acc_email = creds.get("email", "")
                acc_password = creds.get("password", "")

        self.update_status("Navigating to Bing...")
        await self.page.goto("https://bing.com/")

        needs_login = False
        try:
            self.update_status("Checking if already logged in...")
            await asyncio.sleep(random.uniform(2, 3))
            sign_in = self.page.locator("#id_s")
            await sign_in.wait_for(state="visible", timeout=5000)
            needs_login = True
        except Exception:
            self.update_status("Already logged in! Cookies are valid.")

        if needs_login:
            if not acc_email or not acc_password:
                self.update_status(f"Error: Missing credentials for {profile_name}!")
                return

            self.update_status("Logging in...")
            await sign_in.click()

            email_input = self.page.locator('input[type="email"]')
            await email_input.wait_for(state="visible")
            await asyncio.sleep(random.uniform(2, 3))
            await email_input.click()
            await email_input.press_sequentially(acc_email, delay=random.uniform(100, 200))
            await self.page.locator('button[type="submit"]').click()

            try:
                await asyncio.sleep(random.uniform(2, 3))
                other_login_method = self.page.locator("span.fui-Link")
                await other_login_method.wait_for(state="visible", timeout=3000)
                await other_login_method.click()
            except Exception:
                pass

            try:
                await asyncio.sleep(random.uniform(1, 3))
                password_option = self.page.locator('div[aria-label="Use your password"]')
                await password_option.wait_for(state="visible", timeout=3000)
                await password_option.click()
            except Exception:
                pass

            password_input = self.page.locator('input[type="password"]')
            await password_input.wait_for(state="visible")
            await asyncio.sleep(random.uniform(2, 3))
            await password_input.click()
            await password_input.fill(acc_password)
            await self.page.locator('button[type="submit"]').click()

            try:
                await asyncio.sleep(random.uniform(2, 3))
                stay_signed_in_btn = self.page.locator('button.fui-Button:nth-child(2)')
                await stay_signed_in_btn.wait_for(state="visible", timeout=5000)
                await stay_signed_in_btn.click()
            except Exception:
                pass

    async def task_daily_quest(self):
        self.update_status("Doing Daily Quests...")
        for i in range(3, 5):
            await asyncio.sleep(2)
            await self.page.goto("https://www.bing.com//rewards/panelflyout?channel=bingflyout",
                                 referer="https://www.bing.com/")
            try:
                task = self.page.locator(f"#daily_set_card > div:nth-child({i})")
                await task.wait_for(state="visible", timeout=3000)
            except Exception:
                break
            await self.page.set_extra_http_headers({"Referer": "https://www.bing.com//rewards/panelflyout"})
            await task.click()
            await asyncio.sleep(random.uniform(3, 5))
            await self.page.set_extra_http_headers({})

    async def task_daily_search(self):
        self.update_status("Doing Daily Searches...")
        for i in range(1, 9):
            await asyncio.sleep(2)
            if "rewards/panelflyout" not in self.page.url:
                await self.page.goto("https://www.bing.com//rewards/panelflyout?channel=bingflyout",
                                     referer="https://www.bing.com/")
            try:
                daily_search = self.page.locator(f"a.ss_item:nth-child({i})")
                await daily_search.wait_for(state="visible", timeout=3000)
            except Exception:
                break
            await daily_search.click()
            await asyncio.sleep(random.uniform(2, 4))

    async def task_search_trend(self):
        self.update_status("Checking Search Trends...")
        await self.page.goto("https://www.bing.com//rewards/panelflyout?channel=bingflyout",
                             referer="https://www.bing.com/")

        try:
            target_locator = self.page.locator(
                "div.dailycheckin_partnercard:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1) > p:nth-child(1)")
            await target_locator.wait_for(state="visible", timeout=5000)
            check_daily = await target_locator.inner_text()
        except Exception:
            check_daily = ""

        if "3/3" in check_daily:
            self.update_status("Trend searches already completed today.")
            self.disable_trend_btn()
            return

        self.update_status("Executing Trend Searches...")
        await self.page.goto("https://www.bing.com/")

        url = f"https://serpapi.com/search?engine=google_trends_trending_now&geo=VN&api_key={SERPAPI}"
        try:
            response = requests.get(url).json()
            trends = response.get("trending_searches", [])
            search_terms = [item.get("query") for item in trends if item.get("query")]
            random.shuffle(search_terms)
            search_terms = search_terms[:3]
        except Exception:
            search_terms = ["Artificial Intelligence", "Linux gaming", "Python automation"]

        for word in search_terms:
            search_bar = self.page.locator('#sb_form_q')
            await search_bar.wait_for(state="visible", timeout=5000)
            await search_bar.click()
            await search_bar.press_sequentially(f"{word}", delay=200)
            await search_bar.press("Enter")
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(random.uniform(3, 5))
            await search_bar.clear()

        self.update_status("Trend Searches Complete!")
        self.disable_trend_btn()


if __name__ == "__main__":
    app = BingChillingApp()
    app.mainloop()