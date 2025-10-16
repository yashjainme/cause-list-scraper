from flask import Flask, render_template, request, jsonify, send_file, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import time
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Store driver instances per session
drivers = {}

def get_driver(session_id):
    if session_id not in drivers:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        drivers[session_id] = webdriver.Chrome(options=chrome_options)
    return drivers[session_id]

def cleanup_driver(session_id):
    if session_id in drivers:
        try:
            drivers[session_id].quit()
        except:
            pass
        del drivers[session_id]

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
        driver.get(url)
        
        print("\n--- Pausing for 5 seconds to let the page settle ---")
        time.sleep(5)
        
        wait = WebDriverWait(driver, 20)
        
        # Close modal if present
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
        
        # Get states
        state_select_element = wait.until(EC.presence_of_element_located((By.ID, "sess_state_code")))
        state_options = state_select_element.find_elements(By.TAG_NAME, "option")
        
        states = []
        for opt in state_options:
            if opt.get_attribute("value") != "0":
                states.append({
                    "value": opt.get_attribute("value"),
                    "text": opt.text
                })
        
        return jsonify({"success": True, "states": states})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/select_state', methods=['POST'])
def select_state():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        state_value = request.json.get('state_value')
        
        state_select_element = driver.find_element(By.ID, "sess_state_code")
        select_state = Select(state_select_element)
        select_state.select_by_value(state_value)
        
        time.sleep(2)
        
        # Get districts
        district_select_element = driver.find_element(By.ID, "sess_dist_code")
        district_options = district_select_element.find_elements(By.TAG_NAME, "option")
        
        districts = []
        for opt in district_options:
            if opt.get_attribute("value") != "0":
                districts.append({
                    "value": opt.get_attribute("value"),
                    "text": opt.text
                })
        
        return jsonify({"success": True, "districts": districts})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/select_district', methods=['POST'])
def select_district():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        district_value = request.json.get('district_value')
        
        district_select_element = driver.find_element(By.ID, "sess_dist_code")
        select_district = Select(district_select_element)
        select_district.select_by_value(district_value)
        
        time.sleep(2)
        
        # Get court complexes
        court_complex_select_element = driver.find_element(By.ID, "court_complex_code")
        court_complex_options = court_complex_select_element.find_elements(By.TAG_NAME, "option")
        
        court_complexes = []
        for opt in court_complex_options:
            if opt.get_attribute("value") != "0":
                court_complexes.append({
                    "value": opt.get_attribute("value"),
                    "text": opt.text
                })
        
        return jsonify({"success": True, "court_complexes": court_complexes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/select_court_complex', methods=['POST'])
def select_court_complex():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        court_complex_value = request.json.get('court_complex_value')
        
        court_complex_select_element = driver.find_element(By.ID, "court_complex_code")
        select_court_complex = Select(court_complex_select_element)
        select_court_complex.select_by_value(court_complex_value)
        
        time.sleep(2)
        
        # Check for alert and establishments
        establishment_required = False
        establishments = []
        
        try:
            print("\n--- Checking for establishment alert ---")
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"Alert detected: {alert_text}")
            alert.accept()
            print("Alert accepted.")
            establishment_required = True
        except TimeoutException:
            print("No alert detected. Establishment may not be required.")
        except NoAlertPresentException:
            print("No alert present.")
        
        if establishment_required:
            try:
                print("\n--- Waiting for Establishment dropdown ---")
                est_div = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "est_codes"))
                )
                time.sleep(1)
                
                est_select_element = driver.find_element(By.ID, "court_est_code")
                est_options = est_select_element.find_elements(By.TAG_NAME, "option")
                
                for opt in est_options:
                    if opt.get_attribute("value") != "0":
                        establishments.append({
                            "value": opt.get_attribute("value"),
                            "text": opt.text
                        })
            except TimeoutException:
                print("Establishment dropdown did not appear. Continuing...")
        
        return jsonify({
            "success": True, 
            "establishment_required": establishment_required,
            "establishments": establishments
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/select_establishment', methods=['POST'])
def select_establishment():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        establishment_value = request.json.get('establishment_value')
        
        if establishment_value:
            est_select_element = driver.find_element(By.ID, "court_est_code")
            select_est = Select(est_select_element)
            select_est.select_by_value(establishment_value)
            time.sleep(2)
        
        # Get courts
        court_name_select_element = driver.find_element(By.ID, "CL_court_no")
        court_name_options = court_name_select_element.find_elements(By.TAG_NAME, "option")
        
        courts = []
        for opt in court_name_options:
            if opt.get_attribute("value") != "":
                courts.append({
                    "value": opt.get_attribute("value"),
                    "text": opt.text
                })
        
        return jsonify({"success": True, "courts": courts})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/select_court', methods=['POST'])
def select_court():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        court_value = request.json.get('court_value')
        
        court_name_select_element = driver.find_element(By.ID, "CL_court_no")
        select_court_name = Select(court_name_select_element)
        select_court_name.select_by_value(court_value)
        
        time.sleep(1)
        
        # Get date and captcha
        date_input = driver.find_element(By.ID, "causelist_date")
        current_date = date_input.get_attribute("value")
        
        # Get CAPTCHA image as base64
        captcha_img = driver.find_element(By.ID, "captcha_image")
        captcha_base64 = driver.execute_script("""
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var img = arguments[0];
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png');
        """, captcha_img)
        
        return jsonify({
            "success": True,
            "default_date": current_date,
            "captcha_image": captcha_base64
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/refresh_captcha', methods=['POST'])
def refresh_captcha():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        
        # Click refresh using JavaScript since the onclick handler exists
        driver.execute_script("refreshCaptcha();")
        time.sleep(2)
        
        # Get new CAPTCHA image
        captcha_img = driver.find_element(By.ID, "captcha_image")
        captcha_base64 = driver.execute_script("""
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var img = arguments[0];
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png');
        """, captcha_img)
        
        return jsonify({
            "success": True,
            "captcha_image": captcha_base64
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    try:
        session_id = session.get('session_id')
        driver = get_driver(session_id)
        data = request.json
        
        # Set date if provided
        if data.get('date'):
            date_input = driver.find_element(By.ID, "causelist_date")
            date_input.clear()
            date_input.send_keys(data['date'])
            final_date = data['date']
        else:
            date_input = driver.find_element(By.ID, "causelist_date")
            final_date = date_input.get_attribute("value")
        
        # Enter CAPTCHA
        captcha_input = driver.find_element(By.ID, "cause_list_captcha_code")
        captcha_input.clear()
        captcha_input.send_keys(data['captcha'])
        
        time.sleep(1)
        
        # Click appropriate button
        wait = WebDriverWait(driver, 20)
        case_type = data['case_type']
        
        if case_type == 'civil':
            civil_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Civil')]")))
            civil_button.click()
            case_type_title = "Civil"
        else:
            criminal_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Criminal')]")))
            criminal_button.click()
            case_type_title = "Criminal"
        
        print("\n--- Waiting for Cause List Results ---")
        results_div = wait.until(EC.presence_of_element_located((By.ID, "res_cause_list")))
        time.sleep(5)
        
        # Check for no data
        try:
            no_data_element = driver.find_element(By.ID, "nodata")
            if no_data_element.is_displayed():
                return jsonify({"success": False, "error": "No records found for the selected criteria"})
        except:
            pass
        
        # Scrape data
        try:
            table = driver.find_element(By.ID, "dispTable")
        except:
            return jsonify({"success": False, "error": "No data table found in the results"})
        
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
        
        if not cause_list_data:
            return jsonify({"success": False, "error": "No cause list entries were extracted"})
        
        # Generate PDF
        filename = generate_pdf(
            cause_list_data,
            data['state_name'],
            data['district_name'],
            data['court_complex_name'],
            data.get('establishment_name'),
            data['court_name'],
            final_date,
            case_type_title
        )
        
        # Cleanup driver after successful scraping
        cleanup_driver(session_id)
        
        return jsonify({
            "success": True,
            "data": cause_list_data,
            "pdf_file": filename,
            "total_records": len(cause_list_data)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)