from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
import time

def scrape_ecourts_cause_list():
    # --- Configuration ---
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode after implementation of the captcha localization
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the Cause List page
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
        print(f"Navigating to {url}...")
        driver.get(url)

        # --- ADDED: 5-second delay to allow the page to fully load and settle ---
        print("\n--- Pausing for 5 seconds to let the page settle ---")
        time.sleep(5)

        wait = WebDriverWait(driver, 20)

        # --- More reliable modal closing ---
        try:
            print("\n--- Checking for initial modal popup ---")
            modal_close_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-close[data-bs-dismiss='modal']"))
            )
            print("Modal found. Closing it...")
            driver.execute_script("arguments[0].click();", modal_close_button)
            time.sleep(2) 
        except TimeoutException:
            print("Initial modal did not appear, proceeding with script.")
        # --- End of modal handling ---


        # --- Step 1: State Selection ---
        print("\n--- Please select the State ---")
        state_select_element = wait.until(EC.presence_of_element_located((By.ID, "sess_state_code")))
        state_options = state_select_element.find_elements(By.TAG_NAME, "option")
        
        state_names = [opt.text for opt in state_options if opt.get_attribute("value") != "0"]
        for i, name in enumerate(state_names, 1):
            print(f"{i}. {name}")
        state_choice = int(input("Enter the number corresponding to your State: "))
        selected_state_name = state_names[state_choice - 1]
        
        select_state = Select(state_select_element)
        select_state.select_by_visible_text(selected_state_name)
        
        print(f"Selected State: {selected_state_name}")

        # --- Step 2: District Selection ---
        time.sleep(2)
        district_select_element = driver.find_element(By.ID, "sess_dist_code")
        district_options = district_select_element.find_elements(By.TAG_NAME, "option")
        district_names = [opt.text for opt in district_options if opt.get_attribute("value") != "0"]
        print(f"\n--- Please select the District for {selected_state_name} ---")
        for i, name in enumerate(district_names, 1):
            print(f"{i}. {name}")
        district_choice = int(input("Enter the number corresponding to your District: "))
        selected_district_name = district_names[district_choice - 1]

        select_district = Select(district_select_element)
        select_district.select_by_visible_text(selected_district_name)

        print(f"Selected District: {selected_district_name}")

        # --- Step 3: Court Complex Selection ---
        time.sleep(2)
        court_complex_select_element = driver.find_element(By.ID, "court_complex_code")
        court_complex_options = court_complex_select_element.find_elements(By.TAG_NAME, "option")
        court_complex_names = [opt.text for opt in court_complex_options if opt.get_attribute("value") != "0"]
        print(f"\n--- Please select the Court Complex for {selected_district_name} ---")
        for i, name in enumerate(court_complex_names, 1):
           print(f"{i}. {name}")
        court_complex_choice = int(input("Enter the number corresponding to your Court Complex: "))
        selected_court_complex_name = court_complex_names[court_complex_choice - 1]

        select_court_complex = Select(court_complex_select_element)
        select_court_complex.select_by_visible_text(selected_court_complex_name)

        print(f"Selected Court Complex: {selected_court_complex_name}")

        # --- Step 4: Handle Establishment (with Alert handling) ---
        establishment_present = False
        selected_est_name = None
        
        time.sleep(2)
        
        try:
            print("\n--- Checking for establishment alert ---")
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"Alert detected: {alert_text}")
            alert.accept()
            print("Alert accepted.")
            establishment_present = True
        except TimeoutException:
            print("No alert detected. Establishment may not be required.")
        except NoAlertPresentException:
            print("No alert present.")

        if establishment_present:
            try:
                print("\n--- Waiting for Establishment dropdown ---")
                est_div = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "est_codes"))
                )
                time.sleep(1)
                
                est_select_element = driver.find_element(By.ID, "court_est_code")
                est_options = est_select_element.find_elements(By.TAG_NAME, "option")
                est_names = [opt.text for opt in est_options if opt.get_attribute("value") != "0"]
                
                if est_names:
                    print(f"\n--- Please select the Court Establishment ---")
                    for i, name in enumerate(est_names, 1):
                        print(f"{i}. {name}")
                    est_choice = int(input("Enter the number corresponding to your Court Establishment: "))
                    if 1 <= est_choice <= len(est_names):
                        selected_est_name = est_names[est_choice - 1]
                        select_est = Select(est_select_element)
                        select_est.select_by_visible_text(selected_est_name)
                        print(f"Selected Establishment: {selected_est_name}")
                else:
                    print("No establishment options available.")
            except TimeoutException:
                print("Establishment dropdown did not appear. Continuing...")
            except Exception as e:
                print(f"Error handling establishment: {e}")

        # --- Step 5: Court Name Selection ---
        time.sleep(2)
        court_name_select_element = driver.find_element(By.ID, "CL_court_no")
        court_name_options = court_name_select_element.find_elements(By.TAG_NAME, "option")
        court_name_names = [opt.text for opt in court_name_options if opt.get_attribute("value") != ""]
        print(f"\n--- Please select the Court Name ---")
        for i, name in enumerate(court_name_names, 1):
            print(f"{i}. {name}")
        court_name_choice = int(input("Enter the number corresponding to your Court Name: "))
        selected_court_name = court_name_names[court_name_choice - 1]
        
        select_court_name = Select(court_name_select_element)
        select_court_name.select_by_visible_text(selected_court_name)
        
        print(f"Selected Court Name: {selected_court_name}")

        # --- Step 6: Date Selection ---
        date_input = driver.find_element(By.ID, "causelist_date")
        current_date = date_input.get_attribute("value")
        new_date = input(f"\nEnter the Cause List Date (DD-MM-YYYY) [Current: {current_date}, Press Enter to keep]: ")
        if new_date.strip():
            date_input.clear()
            date_input.send_keys(new_date)
            final_date = new_date
            print(f"Set Date to: {new_date}")
        else:
            final_date = current_date
            print(f"Keeping default Date: {current_date}")

        # --- Step 7: CAPTCHA Handling ---
        captcha_img = wait.until(EC.presence_of_element_located((By.ID, "captcha_image")))
        print(f"\n--- CAPTCHA IMAGE ---")
        print("Please look at the CAPTCHA image displayed in the browser window.")
        captcha_text = input("Enter CAPTCHA: ").strip()
        captcha_input = driver.find_element(By.ID, "cause_list_captcha_code")
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        print(f"Entered CAPTCHA: {captcha_text}")

        # --- Step 8: Submit Form ---
        print("\n--- Submitting Form ---")
        civil_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Civil')]")))
        criminal_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Criminal')]")))

        choice = input("Choose 'Civil' or 'Criminal' (Enter 'c' for Civil, 'r' for Criminal): ").lower().strip()
        case_type = ""
        if choice == 'c':
            civil_button.click()
            case_type = "Civil"
            print("Clicked 'Civil' button.")
        elif choice == 'r':
            criminal_button.click()
            case_type = "Criminal"
            print("Clicked 'Criminal' button.")
        else:
            print("Invalid choice. Defaulting to 'Civil'.")
            civil_button.click()
            case_type = "Civil"

        # --- Step 9: Wait for Results and Scrape Data ---
        print("\n--- Waiting for Cause List Results ---")
        results_div = wait.until(EC.presence_of_element_located((By.ID, "res_cause_list")))
        time.sleep(5)

        try:
            no_data_element = driver.find_element(By.ID, "nodata")
            if no_data_element.is_displayed():
                print("\n⚠ No records found for the selected criteria.")
                return
        except:
            pass

        try:
            table = driver.find_element(By.ID, "dispTable")
        except:
            print("\n⚠ No data table found in the results.")
            return

        rows = table.find_elements(By.TAG_NAME, "tr")

        cause_list_data = []
        current_category = None

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                cell_html = cells[0].get_attribute('outerHTML')
                if 'color:#3880d4' in cell_html and 'colspan' in cell_html:
                    category_text = cells[0].text.strip()
                    if category_text:
                        current_category = category_text
                        continue

                if len(cells) >= 4:
                    sr_no = cells[0].text.strip()
                    case_info_cell = cells[1]
                    party_cell = cells[2]
                    advocate_cell = cells[3]

                    case_link = None
                    case_number = ""
                    next_hearing = ""

                    if case_info_cell:
                        try:
                            view_link = case_info_cell.find_element(By.TAG_NAME, "a")
                            case_link = view_link.get_attribute("href")
                        except:
                            pass
                        
                        text_parts = [part.strip() for part in case_info_cell.text.split('\n') if part.strip()]
                        for part in text_parts:
                            if part.lower() == 'view':
                                continue 
                            elif 'next hearing date' in part.lower():
                                next_hearing = part.replace('Next hearing date:-', '').strip()
                            else:
                                case_number = part 


                    party_name = party_cell.text.strip() if party_cell else ""
                    advocate_name = advocate_cell.text.strip() if advocate_cell else ""

                    row_data = {
                        "Sr No": sr_no,
                        "Category": current_category,
                        "Case Link": case_link,
                        "Case Number": case_number,
                        "Next Hearing Date": next_hearing,
                        "Party Name": party_name,
                        "Advocate": advocate_name
                    }
                    cause_list_data.append(row_data)

        # --- Step 10: Display Results ---
        print(f"\n--- Scraped {len(cause_list_data)} Cause List Entries ---")
        
        if not cause_list_data:
            print("\n⚠ No cause list entries were extracted.")
            return
        
        for entry in cause_list_data:
            print(f"SR NO: {entry['Sr No']}")
            print(f"  Category: {entry['Category']}")
            print(f"  Case Number: {entry['Case Number']}")
            print(f"  Next Hearing Date: {entry['Next Hearing Date']}")
            print(f"  Party Name: {entry['Party Name']}")
            print(f"  Advocate: {entry['Advocate']}")
            print(f"  View Link: {entry['Case Link']}")
            print("-" * 50)

        # --- Step 11: Generate PDF ---
        generate_pdf(
            cause_list_data,
            selected_state_name,
            selected_district_name,
            selected_court_complex_name,
            selected_est_name,
            selected_court_name,
            final_date,
            case_type
        )

        print("\nScraping completed successfully!")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'driver' in locals() and driver:
            driver.quit()
        print("Browser closed.")


def generate_pdf(data, state, district, court_complex, establishment, court_name, date, case_type):
    """Generate a PDF report from the scraped cause list data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"CauseList_{case_type}_{date.replace('-', '')}_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        alignment=1
    )
    
    title = Paragraph(f"<b>eCourts Cause List - {case_type}</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Court Details
    detail_style = ParagraphStyle('Details', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    
    details = [
        f"<b>State:</b> {state}", f"<b>District:</b> {district}",
        f"<b>Court Complex:</b> {court_complex}",
    ]
    if establishment:
        details.append(f"<b>Establishment:</b> {establishment}")
    details.extend([
        f"<b>Court Name:</b> {court_name}", f"<b>Date:</b> {date}",
        f"<b>Generated on:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    ])
    
    for detail in details:
        elements.append(Paragraph(detail, detail_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Group data by category
    categories = {}
    for entry in data:
        cat = entry['Category'] or 'Uncategorized'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)
    
    # Create tables for each category
    for category, entries in categories.items():
        cat_style = ParagraphStyle(
            'Category', parent=styles['Heading2'], fontSize=12,
            textColor=colors.HexColor('#3880d4'), spaceAfter=8
        )
        elements.append(Paragraph(f"<b>{category}</b>", cat_style))
        
        table_data = [['Sr No', 'Case Number', 'Next Hearing', 'Party Name', 'Advocate']]
        
        for entry in entries:
            table_data.append([
                entry['Sr No'],
                entry['Case Number'],
                entry['Next Hearing Date'],
                entry['Party Name'][:50] + '...' if len(entry['Party Name']) > 50 else entry['Party Name'],
                entry['Advocate'][:30] + '...' if len(entry['Advocate']) > 30 else entry['Advocate']
            ])
        
        table = Table(table_data, colWidths=[0.6*inch, 1.8*inch, 1.2*inch, 2.8*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
    
    doc.build(elements)
    print(f"\n✓ PDF generated successfully: {filename}")
    return filename

# Run the scraper
if __name__ == "__main__":
    scrape_ecourts_cause_list()