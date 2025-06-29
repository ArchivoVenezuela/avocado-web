import os
import csv
import time
import requests
import json
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, redirect, send_file, render_template, flash

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-me-please-for-production')

def get_token(wskey, wssecret):
    """Get OCLC token with provided credentials"""
    try:
        resp = requests.post(
            'https://oauth.oclc.org/token',
            auth=(wskey, wssecret),
            data={'grant_type': 'client_credentials', 'scope': 'wcapi:view_bib'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get('access_token')
        return None
    except Exception:
        return None

def search_oclc(title, author, token):
    """Search for OCLC number with multiple strategies"""
    # Clean search terms
    title_clean = title.strip()
    author_clean = author.strip()
    
    # Multiple search strategies
    queries = [
        f'ti:"{title_clean}" AND au:"{author_clean}"',
        f'ti:{title_clean} AND au:{author_clean}',
        f'"{title_clean}" AND "{author_clean}"',
        f'{title_clean} {author_clean}',
    ]
    
    for query in queries:
        try:
            url = 'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs'
            params = {
                'q': query,
                'limit': 10,
                'offset': 1,
                'orderBy': 'bestMatch'
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                bib_records = data.get('bibRecords', [])
                if bib_records:
                    identifier = bib_records[0].get('identifier', {})
                    oclc_number = identifier.get('oclcNumber')
                    if oclc_number:
                        return str(oclc_number)
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception:
            continue
    
    return None

def fetch_metadata(oclc, token):
    """Fetch complete metadata for OCLC number"""
    try:
        url = f'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/{oclc}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        resp = requests.get(url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

def clean_text(text):
    """Clean text for output"""
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    import unicodedata, re
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def parse_metadata(json_data, oclc):
    """Parse complete metadata from JSON response"""
    record = {
        'OCLC #': str(oclc),
        'Title': '',
        'Creator': '',
        'Publisher': '',
        'Date': '',
        'Language': '',
        'Subjects': '',
        'Type': '',
        'Format': '',
        'ISBN': '',
        'ISSN': '',
        'Edition': '',
        'URL': f'https://www.worldcat.org/oclc/{oclc}'
    }
    
    try:
        if not json_data:
            return record
        
        # Title extraction
        title_data = json_data.get('title', {})
        if isinstance(title_data, dict):
            main_titles = title_data.get('mainTitles', [])
            if main_titles and isinstance(main_titles, list) and len(main_titles) > 0:
                first_title = main_titles[0]
                if isinstance(first_title, dict):
                    title_text = first_title.get('text', '')
                    if title_text:
                        clean_title = title_text.split(' / ')[0].strip()
                        record['Title'] = clean_text(clean_title)
        
        # Creator extraction
        contributor_data = json_data.get('contributor', {})
        if isinstance(contributor_data, dict):
            creators = contributor_data.get('creators', [])
            if creators and isinstance(creators, list) and len(creators) > 0:
                creator = creators[0]
                if isinstance(creator, dict):
                    first_name = ""
                    last_name = ""
                    
                    if "firstName" in creator and isinstance(creator["firstName"], dict):
                        first_name = creator["firstName"].get("text", "")
                    if "secondName" in creator and isinstance(creator["secondName"], dict):
                        last_name = creator["secondName"].get("text", "")
                    
                    full_name = f"{first_name} {last_name}".strip()
                    if full_name:
                        record['Creator'] = clean_text(full_name)
        
        # Publisher extraction - multiple methods
        publisher = ""
        
        # Method 1: publishers array
        publishers = json_data.get('publishers', [])
        if publishers and isinstance(publishers, list) and len(publishers) > 0:
            pub = publishers[0]
            if isinstance(pub, dict):
                pub_name = pub.get('publisherName', {})
                if isinstance(pub_name, dict):
                    publisher = pub_name.get('text', '')
        
        # Method 2: publication array
        if not publisher:
            publication = json_data.get('publication', [])
            if publication and isinstance(publication, list) and len(publication) > 0:
                pub = publication[0]
                if isinstance(pub, dict):
                    pub_text = pub.get('publisher', '')
                    if pub_text:
                        publisher = str(pub_text)
        
        # Method 3: direct publisher field
        if not publisher:
            pub_direct = json_data.get('publisher')
            if pub_direct:
                if isinstance(pub_direct, list) and pub_direct:
                    publisher = str(pub_direct[0])
                elif isinstance(pub_direct, str):
                    publisher = pub_direct
        
        record['Publisher'] = clean_text(publisher)
        
        # Date
        date_data = json_data.get('date', {})
        if isinstance(date_data, dict):
            pub_date = date_data.get('publicationDate', '')
            if pub_date:
                record['Date'] = str(pub_date)
        
        # Language
        languages = json_data.get('language', [])
        if languages and isinstance(languages, list) and len(languages) > 0:
            lang = languages[0]
            if isinstance(lang, dict):
                lang_code = lang.get('languageCode', '')
                if lang_code:
                    record['Language'] = str(lang_code)
            elif isinstance(lang, str):
                record['Language'] = lang
        
        # Subjects
        subjects = json_data.get('subject', [])
        subject_list = []
        if subjects and isinstance(subjects, list):
            for subj in subjects[:5]:
                if isinstance(subj, dict):
                    subj_name = subj.get('subjectName', {})
                    if isinstance(subj_name, dict):
                        subj_text = subj_name.get('text', '')
                        if subj_text:
                            subject_list.append(clean_text(subj_text))
                elif isinstance(subj, str):
                    subject_list.append(clean_text(subj))
        record['Subjects'] = ' ; '.join(subject_list)
        
        # Type
        item_type = json_data.get('itemType', {})
        if isinstance(item_type, dict):
            type_text = item_type.get('text', '')
            if type_text:
                record['Type'] = str(type_text)
        
        # Format
        formats = json_data.get('format', [])
        if formats and isinstance(formats, list) and len(formats) > 0:
            fmt = formats[0]
            if isinstance(fmt, dict):
                fmt_text = fmt.get('text', '')
                if fmt_text:
                    record['Format'] = str(fmt_text)
            elif isinstance(fmt, str):
                record['Format'] = fmt
        
        # ISBN/ISSN extraction
        isbn_list = []
        issn_list = []
        
        identifier = json_data.get('identifier', {})
        if isinstance(identifier, dict):
            # Direct lists
            isbns = identifier.get('isbns', [])
            if isinstance(isbns, list):
                isbn_list.extend([str(isbn) for isbn in isbns if isbn])
            
            issns = identifier.get('issns', [])
            if isinstance(issns, list):
                issn_list.extend([str(issn) for issn in issns if issn])
            
            # Items array
            items = identifier.get('items', [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        item_type = item.get('type', '').lower()
                        value = item.get('value', '')
                        if item_type == 'isbn' and value:
                            isbn_list.append(str(value))
                        elif item_type == 'issn' and value:
                            issn_list.append(str(value))
        
        # Clean and deduplicate
        if isbn_list:
            record['ISBN'] = '; '.join(sorted(set(isbn_list)))
        if issn_list:
            record['ISSN'] = '; '.join(sorted(set(issn_list)))
        
        # Edition
        edition_info = json_data.get('edition', '')
        if isinstance(edition_info, list) and edition_info:
            edition_info = edition_info[0]
        if isinstance(edition_info, dict):
            edition_info = edition_info.get('text', '')
        if edition_info:
            record['Edition'] = clean_text(str(edition_info))
        
        return record
        
    except Exception:
        return record

@app.route('/download-template')
def download_template():
    """Download CSV template"""
    try:
        template_content = """OCLC #,Author,Title
,García Márquez, Gabriel,Cien años de soledad
,Allende, Isabel,La casa de los espíritus
,Vargas Llosa, Mario,Conversación en la catedral
,Borges, Jorge Luis,Ficciones
,Cortázar, Julio,Rayuela
,Carpentier, Alejo,El reino de este mundo
,Fuentes, Carlos,La muerte de Artemio Cruz
,Uslar Pietri, Arturo,Las lanzas coloradas
,Gallegos, Rómulo,Doña Bárbara
,Díaz Rodríguez, Manuel,Ídolos rotos"""
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig')
        temp_file.write(template_content)
        temp_file.close()
        
        return send_file(
            temp_file.name, 
            as_attachment=True, 
            download_name='avocado_template.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f"Error creating template: {str(e)}", 'error')
        return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get credentials from form
            wskey = request.form.get('wskey', '').strip()
            wssecret = request.form.get('wssecret', '').strip()
            
            # Fallback to environment variables if not provided in form
            if not wskey:
                wskey = os.getenv('OCLC_WSKEY', '').strip()
            if not wssecret:
                wssecret = os.getenv('OCLC_WSSECRET', '').strip()
            
            if not wskey or not wssecret:
                flash("Please provide both OCLC WSKey and Secret", 'error')
                return redirect('/')
            
            # Get uploaded file
            file = request.files.get('csv_file')
            if not file or file.filename == '':
                flash("Please select a CSV file", 'error')
                return redirect('/')
            
            # Read CSV file
            try:
                import io
                stream = io.TextIOWrapper(file.stream, encoding='utf-8-sig')
                reader = csv.DictReader(stream)
                rows = list(reader)
                
                if not rows:
                    flash("CSV file is empty", 'error')
                    return redirect('/')
                
                # Validate headers
                expected_headers = {'OCLC #', 'Author', 'Title'}
                actual_headers = set(reader.fieldnames) if reader.fieldnames else set()
                missing_headers = expected_headers - actual_headers
                
                if missing_headers:
                    flash(f"CSV must contain columns: {', '.join(missing_headers)}", 'error')
                    return redirect('/')
                
            except Exception as e:
                flash(f"Error reading CSV file: {str(e)}", 'error')
                return redirect('/')
            
            # Get OCLC token
            token = get_token(wskey, wssecret)
            if not token:
                flash("Authentication with OCLC failed. Please check your credentials.", 'error')
                return redirect('/')
            
            # Process rows
            results = []
            processed_count = 0
            found_oclc_count = 0
            metadata_complete_count = 0
            
            for row in rows:
                title = row.get('Title', '').strip()
                author = row.get('Author', '').strip()
                
                if not title and not author:
                    continue  # Skip completely empty rows
                
                processed_count += 1
                existing_oclc = row.get('OCLC #', '').strip()
                
                # Search for OCLC number if not provided
                oclc_number = existing_oclc
                if not oclc_number and title and author:
                    oclc_number = search_oclc(title, author, token)
                    time.sleep(0.3)  # Rate limiting
                
                if oclc_number:
                    found_oclc_count += 1
                    # Fetch complete metadata
                    metadata = fetch_metadata(oclc_number, token)
                    record = parse_metadata(metadata or {}, oclc_number)
                    
                    # Check if we got complete metadata
                    if record.get('Title') and record.get('Publisher'):
                        metadata_complete_count += 1
                    
                    results.append(record)
                    time.sleep(0.3)  # Rate limiting
                else:
                    # Create basic record without OCLC
                    record = {
                        'OCLC #': '',
                        'Title': title,
                        'Creator': author,
                        'Publisher': '',
                        'Date': '',
                        'Language': '',
                        'Subjects': '',
                        'Type': '',
                        'Format': '',
                        'ISBN': '',
                        'ISSN': '',
                        'Edition': '',
                        'URL': ''
                    }
                    results.append(record)
            
            if not results:
                flash("No valid rows to process", 'error')
                return redirect('/')
            
            # Create output file
            try:
                # Use absolute path in temp directory
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w', 
                    suffix='.csv', 
                    delete=False, 
                    encoding='utf-8-sig'
                )
                
                fieldnames = [
                    'OCLC #', 'Title', 'Creator', 'Publisher', 'Date', 
                    'Language', 'Subjects', 'Type', 'Format', 
                    'ISBN', 'ISSN', 'Edition', 'URL'
                ]
                
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
                temp_file.close()
                
                # Add statistics to flash message
                flash(
                    f"Processing complete! "
                    f"Total: {len(results)} | "
                    f"OCLC found: {found_oclc_count} | "
                    f"Complete metadata: {metadata_complete_count}",
                    'success'
                )
                
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name='avocado_output.csv',
                    mimetype='text/csv'
                )
                
            except Exception as e:
                flash(f"Error creating output file: {str(e)}", 'error')
                return redirect('/')
        
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect('/')
    
    # GET request - show form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)