import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static', template_folder='templates')

# Load the dataset
data = pd.read_excel('C:/Users/harsh/OneDrive/Desktop/MajorP-I/Medical_plants1.xlsx')

@app.route('/')
def index_v2():
    # Render index_v2.html as the main page
    return render_template('index_v2.html')

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'GET':
        # This renders the search form
        return render_template('search.html')

    if request.method == 'POST':
        # This handles the form submission
        search_term = request.form['search_term']
        search_option = request.form['search_option']

        try:
            # Ensure search term is not empty
            if not search_term:
                return render_template('result.html', results="Please enter a search term.")

            # Determine the search type
            if search_option in ['Botanical Name', 'Common Name(s)']:
                result = data[data[search_option].str.contains(search_term, case=False, na=False)]
                # Display all info for these columns
            elif search_option in ['Medicinal Uses', 'Active Compounds', 'Method of Preparation']:
                result = data[data[search_option].str.contains(search_term, case=False, na=False)]
                # Show specific columns
                result = result[['Botanical Name', 'Common Name(s)', 'Medicinal Uses', 'Active Compounds', 'Method of Preparation']]
            else:
                result = data[data[search_option].str.contains(search_term, case=False, na=False)]
                result = result[['Botanical Name','Common Name(s)', search_option]]

            if result.empty:
                return render_template('result.html', results="No results found.")

            return render_template('result.html', results=result.to_html(index=False))

        except Exception as e:
            print(f"Error: {e}")
            return render_template('result.html', results="An error occurred while processing your request. Please check the console for details.")

@app.route('/search_page')
def search_page():
    # This route will render the search form page (search.html) when clicking 'search' from index_v2
    return render_template('search.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

# 🆕 New Route for Docs Page
@app.route('/docs')
def docs():
    return render_template('docs.html')

# 🆕 New Route for Ayurveda Page
@app.route('/ayurveda')
def ayurveda():
    return render_template('ayurveda.html')  # This will render the Ayurveda page

# 🆕 New Route for Yoga Page
@app.route('/yoga')
def yoga():
    return render_template('yoga.html')  # This will render the Yoga page

# 🆕 New Route for Naturopathy Page
@app.route('/naturopathy')
def naturopath():
    return render_template('naturopathy.html')  

# 🆕 New Route for Unani Page
@app.route('/unani')
def unani():
    return render_template('unani.html')  

# 🆕 New Route for Siddha Page
@app.route('/siddha')
def siddha():
    return render_template('siddha.html')  

# 🆕 New Route for Homeopathy Page
@app.route('/homeopathy')
def homeopathy():
    return render_template('homeopathy.html')  


@app.route('/back_to_home')
def back_to_home():
    # This route will take user back to index_v2.html from result.html
    return render_template('index_v2.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
