from flask import Flask, render_template, request, jsonify
import os
import csv
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/autocomplete')
def autocomplete():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    filename =  os.path.join(file_dir, 'sample_data/centers_grade12_2081.tsv')
    data = {}

    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            data[row['cscode']] = row['name']
    
    term = request.args.get('term', '')
    results = {key: value for key, value in data.items() if term.lower() in value.lower()}
    return jsonify(results)

@app.route('/school-exam-centers')
def school_exam_centers():
    scode = request.args.get('scode',0, type=int)
    data = []
    if scode > 0:
        # to run in viratual environment
        #cmd = f'source venv/bin/activate python school_center.py ./sample_data/schools_grade12_2081.tsv  ./sample_data/centers_grade12_2081.tsv  ./sample_data/prefs.tsv -o school-center.tsv -s {scode}'
        cmd = f'python3 school_center.py ./sample_data/schools_grade12_2081.tsv  ./sample_data/centers_grade12_2081.tsv  ./sample_data/prefs.tsv -o school-center.tsv -s {scode}'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
     
        file_dir = os.path.dirname(os.path.abspath(__file__))
        filename =  os.path.join(file_dir, 'results/school-center.tsv')
        
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                if int(row['scode']) == scode:
                    data.append({'cscode': row['cscode'], 'center': row['center'], 'center_address': row['center_address']})
    if len(data)>0:
        rendered_template = render_template('centers.html', data=data)
        return jsonify(data=rendered_template)
    
    return jsonify(data=None)
    
@app.route("/exam-centers")
def exam_centers():
    # Read TSV file and split into chunks
    file_dir = os.path.dirname(os.path.abspath(__file__))
    filename =  os.path.join(file_dir, 'sample_data/centers_grade12_2081.tsv')
    data = read_tsv(filename)

    # Sort data by 'name' column
    data.sort(key=lambda x: x['name'])

    # Pagination
    page = request.args.get('page', 1, type=int)
    chunk_size = 10
    start_index = (page - 1) * chunk_size
    end_index = min(start_index + chunk_size, len(data))
    chunked_data = data[start_index:end_index]

    # Calculate total pages
    total_pages = (len(data) + chunk_size - 1) // chunk_size

    return render_template('exam_centers.html', data=chunked_data, page=page, total_pages=total_pages)

def read_tsv(file_path: str):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            data.append(dict(row))
    return data

if __name__ == "__main__":
    app.run(debug=True) 

# for development server: $ python app.py   
# from flask : flask --app app run    
