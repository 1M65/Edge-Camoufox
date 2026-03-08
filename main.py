import asyncio
import os

import requests
import random
from dotenv import load_dotenv
from camoufox.async_api import AsyncCamoufox
from platformdirs import user_data_dir
from browserforge.fingerprints import Screen

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SERPAPI = os.getenv("SERPAPI_KEY")

async def main():
    constrains = Screen(max_width=1280, max_height=720)
    # 1. user_data_dir creates a persistent profile folder to save cookies automatically
    async with AsyncCamoufox(
            screen=constrains,
            headless=False,
            humanize=2.0,
            persistent_context=True,
            user_data_dir="bing_profile"
    ) as browser:
        #SERPAPI
        print(SERPAPI)
        def trending_words(count=3):

            url = f"https://serpapi.com/search?engine=google_trends_trending_now&geo=VN&api_key={SERPAPI}"
            try:
                response = requests.get(url).json()
                trends = response.get("trending_searches", [])
                trending_list = [item.get("query") for item in trends if item.get("query")]
                random.shuffle(trending_list)
                return trending_list[:count]

            except Exception as e:
                print(e)
                return ["Artificial Intelligence", "Linux gaming", "Python automation"]
        print(trending_words(3))


        search_terms =  trending_words(3)
        # Get the default page from the persistent context
        pages = browser.pages
        page = pages[0] if pages else await browser.new_page()

        print("Navigating to Bing...")
        await page.goto("https://bing.com/")

        # 2. Check if we need to log in
        needs_login = False
        try:
            print("Checking if already logged in...")
            # Look for the Rewards button. We only wait 5 seconds.
            sign_in = page.get_by_text("Sign in")
            await rewards.wait_for(state="visible", timeout=5000)
            needs_login = True  # If we find it, we need to log in
        except Exception:
            print("Rewards button not found. Assuming we are already logged in!")

        # 3. Execute login ONLY if needed
        if needs_login:
            print("Not logged in. Starting login process...")
            await sign_in.click()

            # Email
            email_input = page.locator('input[type="email"]')
            await email_input.wait_for(state="visible")
            await asyncio.sleep(1)
            print("Typing email...")
            await email_input.click()
            await email_input.press_sequentially(f"{EMAIL}", delay=120)
            await page.locator('button[type="submit"]').click()

            # Check alter sign-in
            try:
                alt_link = page.locator('span.fui-Link')
                await alt_link.wait_for(state="visible", timeout=3000)
                await alt_link.click()

                password_option = page.locator('div[aria-label="Use your password"]')
                await password_option.wait_for(state="visible", timeout=3000)
                await password_option.click()
            except Exception:
                pass

            # Password
            password_input = page.locator('input[type="password"]')
            await password_input.wait_for(state="visible")
            await asyncio.sleep(1.5)
            print("Typing password...")
            await password_input.click()
            await password_input.press_sequentially(f"{PASSWORD}", delay=100)
            await page.locator('button[type="submit"]').click()

            # Stay signed in?
            try:
                stay_signed_in_btn = page.locator('input[id="idSIButton9"]')
                await stay_signed_in_btn.wait_for(state="visible", timeout=5000)
                await stay_signed_in_btn.click()
            except Exception:
                pass

            print("Login complete! Cookies are now saved in the 'bing_profile' folder.")

        # --- YOUR AUTOMATION CODE GOES HERE ---
        print("Ready to start automating tasks!")

        # await page.goto("https://www.bing.com//rewards/panelflyout?channel=bingflyout&partnerId=BingRewards&isDarkMode=0&ru=https%3A%2F%2Fwww.bing.com%2F", referer="https://www.bing.com/")








        #SEARCH
        # for word in search_terms:
        #
        #     search_bar = page.locator('#sb_form_q')
        #     await search_bar.wait_for(state="visible", timeout=5000)
        #     await search_bar.click()
        #     await search_bar.press_sequentially(f"{word}", delay=200)
        #     await search_bar.press("Enter")
        #     await page.wait_for_load_state("networkidle")
        #     wait_time = random.uniform(3, 5)
        #     await asyncio.sleep(wait_time)
        #     await search_bar.clear()

        # Keep browser open to verify
        await page.wait_for_event("close")


if __name__ == "__main__":
    asyncio.run(main())