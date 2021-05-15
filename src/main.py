import traceback
from time import sleep, time
from selenium.common.exceptions import InvalidSessionIdException
from config.user_details import phone, location, additional_members

from src.telegram_utils import *
from src.gen_utils import *

phone_number = phone['number']
bot_token = phone['telegram_token']

chat_id = initialize_bot(bot_token)

user_state = location['state']
user_area = location['district']

landing_page = 'https://selfregistration.cowin.gov.in/'


def start_session():

	browser.get(landing_page)

	retry_till_find_element_by_tag_name(browser, 'input').send_keys(phone_number)
	req_otp_timestamp = time()
	browser.find_element_by_class_name('covid-button-desktop').click()
	send_message(bot_token, "Enter OTP to login.", chat_id)

	print('Waiting for OTP on telegram ...')
	msg_timestamp = 1
	while msg_timestamp < req_otp_timestamp:
		last_incoming_message, msg_timestamp, _ = get_last_chat_id_and_text(get_updates(bot_token))
		sleep(1)

	browser.find_element_by_tag_name('input').send_keys(last_incoming_message)
	browser.find_element_by_class_name('covid-button-desktop').click()

	session_start_time = time()
	send_message(bot_token, f"Logged into application.", chat_id)

	# Click on Schedule
	retry_click(find_first_schedule_button(browser))

	for member in additional_members:
		browser.retry_till_find_elements_by_class_name('chk-box')[member].click()
		sleep(0.8)

	# Click on 'Schedule Now' at the bottom
	retry_till_find_element_by_class_name(browser, 'book-btn').click()

	sleep(3)

	while (time() - session_start_time) < (60.0 * 13):
		retry_click(retry_till_find_element_by_class_name(browser, 'status-switch'))  # Switch to Search by District
		sleep(0.5)

		# Select state
		retry_till_find_element_by_class_name(browser, 'mat-form-field-wrapper').click()
		retry_click(next(iter([i for i in retry_till_find_elements_by_class_name(browser, 'mat-option-text') if user_state in i.text])))

		sleep(0.5)
		# Select district
		retry_click(retry_till_find_elements_by_class_name(browser, 'mat-form-field-wrapper')[1])
		retry_click(next(iter([i for i in retry_till_find_elements_by_class_name(browser, 'mat-option-text') if user_area in i.text])))
		sleep(0.5)

		# Click on search
		retry_click(retry_till_find_element_by_class_name(browser, 'district-search'))

		retry_click(next(iter([i for i in retry_till_find_elements_by_tag_name(browser, 'label') if i.text == 'Age 18+'])))
		sleep(1)

		all_rows = browser.find_elements_by_class_name('mat-list-item-content')
		for row in all_rows:
			# For block code might be outdated since author doesn't have access to slots page anymore after vaccination

			cells = row.find_elements_by_class_name('slots-box')
			cells_18 = [i for i in cells if 'Age 18+' in i.text]  # cells for 18+
			if len(cells_18) > 0:
				center_name = row.find_element_by_class_name('center-name-title').text
				print('\n18+ center:', center_name, end='')
			for cell in cells_18:
				open_count = cell.find_element_by_tag_name('a').text
				if 'Booked' not in open_count:   # Finds a slot
					send_message(bot_token, f"{open_count} slot(s) open for {center_name}!", chat_id)
					cell.find_element_by_tag_name('a').click()  # Click to go to the next page
					sleep(1)

					retry_click(retry_till_find_element_by_class_name(browser, 'time-slot'))
					# warning: will get stuck if the first time slot is not clickable
					sleep(0.5)

					# Enter captcha at this point on the UI
					send_message(bot_token, f"Enter captcha on UI.", chat_id)
					input('\nProceed after captcha?')

					retry_click(retry_till_find_element_by_class_name(browser, 'register-btn'))
					send_message(bot_token, f"Confirm button clicked.", chat_id)

					return

				else:
					print(' Booked', end='')

		print('\nCompleted search; refreshing for another round ...')
		browser.refresh()

	send_message(bot_token, f"13m elapsed, good time to restart new session.", chat_id)
	browser.close()


if __name__ == "__main__":

	while True:
		try:
			browser = launch_browser()
			start_session()
		except Exception:
			try:
				browser.close()
			except InvalidSessionIdException:
				pass

			print(traceback.format_exc())
			send_message(bot_token, f"Caught exception, auto-restarting browser ... ", chat_id)
			sleep(10)
		else:
			resp = input('\nClose and run again? y/n')
			if resp.lower == 'y':
				browser.close()
				continue
			else:
				break
