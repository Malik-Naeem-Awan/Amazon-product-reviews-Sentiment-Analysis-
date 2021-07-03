import tensorflow
from flask import Flask, render_template, request
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import numpy as np
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

app = Flask(__name__)


def web_scrap(url):
    global model
    model = load_model('BILSTM_Model.h5')
    global x
    x = 0
    productURLinput = url

    options = Options()

    options.headless = True

    driver = webdriver.Chrome(executable_path='edgedriver_win64/chromedriver.exe', options=options)

    driver.get(productURLinput)

    try:
        if driver.find_element_by_link_text('See all reviews'):
            link = driver.find_element_by_link_text('See all reviews')
            link.click()

    except NoSuchElementException:
        x = -1
        print("No Reviews Found in this page :(")
        return x
    if x is -1:
        return x
    else:
        productURLinput = driver.current_url

        extractor = driver.find_element_by_xpath('//div[@class="a-row a-spacing-base a-size-base"]').text.split(" | ")

        total_reviews_extractor = extractor[1].split()
        total_reviews_extractor[0] = total_reviews_extractor[0].replace(',', '').strip()
        print(total_reviews_extractor[0])

        total_reviews = int(total_reviews_extractor[0])

        if (total_reviews / 10).is_integer():

            total_pages = int(total_reviews / 10)

        else:

            total_pages = int(total_reviews / 10) + 1

        Review_record = []

        for pg in range(1, total_pages + 1):

            ####################################################################################

            link = productURLinput + "&pageNumber=" + str(pg)
            driver.get(link)

            soup = bs(driver.page_source, 'html.parser')
            soup.prettify()

            ####################################################################################
            print("Scrapping Page " + str(pg) + " Please wait...")

            def extract_data(items):

                try:

                    cust_names = items.find('span', class_="a-profile-name").text

                except AttributeError:
                    cust_names = ''
                #######################################################################
                try:

                    date = items.find('span', {"data-hook": "review-date"}).text

                except AttributeError:
                    date = ''
                ##############################################################################
                try:

                    title = items.find('a', class_='review-title-content').text

                    review_title = []
                    review_title.append(title)

                    review_title[:] = [titles.lstrip('\n') for titles in review_title]

                    review_title[:] = [titles.rstrip('\n') for titles in review_title]

                    title = review_title[0]

                except AttributeError:
                    title = ''

                try:

                    rating = items.find('i', class_='review-rating').text

                except AttributeError:
                    rating = ''

                try:

                    review = items.find("span", {"data-hook": "review-body"}).text

                    review_content = []
                    review_content.append(review)

                    review_content[:] = [reviews.lstrip('\n') for reviews in review_content]

                    review_content[:] = [reviews.rstrip('\n') for reviews in review_content]

                    review = review_content[0]


                except AttributeError:
                    review = ''

                record = (cust_names, title, rating, review, date)

                return record

            ####################################################################################

            results = soup.find_all('div', class_="a-section celwidget")

            for items in results:
                R_record = extract_data(items)

                if R_record:
                    Review_record.append(R_record)

            ####################################################

        driver.close()

        print()
        print("**************************************************************")
        print("*                                                            *")
        print("             Scrapping Done Saving it into Dataframe          ")
        print("*                                                            *")
        print("**************************************************************")

        scrapped_df = pd.DataFrame(Review_record, columns=["Customer Name", "Review Title", "Rating", "Review", "Date"])

        scrapped_df.loc[scrapped_df['Date'].str.contains("January"), 'Date'] = scrapped_df['Date'].str.slice(-16, None,
                                                                                                             1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("February"), 'Date'] = scrapped_df['Date'].str.slice(-17, None,
                                                                                                              1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("March"), 'Date'] = scrapped_df['Date'].str.slice(-14, None, 1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("April"), 'Date'] = scrapped_df['Date'].str.slice(-14, None, 1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("May"), 'Date'] = scrapped_df['Date'].str.slice(-12, None, 1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("June"), 'Date'] = scrapped_df['Date'].str.slice(-13, None, 1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("July"), 'Date'] = scrapped_df['Date'].str.slice(-13, None, 1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("August"), 'Date'] = scrapped_df['Date'].str.slice(-15, None,
                                                                                                            1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("September"), 'Date'] = scrapped_df['Date'].str.slice(-18,
                                                                                                               None, 1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("October"), 'Date'] = scrapped_df['Date'].str.slice(-16, None,
                                                                                                             1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("November"), 'Date'] = scrapped_df['Date'].str.slice(-17, None,
                                                                                                              1)
        scrapped_df.loc[scrapped_df['Date'].str.contains("December"), 'Date'] = scrapped_df['Date'].str.slice(-17, None,
                                                                                                              1)
        scrapped_df['Rating'] = scrapped_df['Rating'].str.slice(0, 3, 1)

        html = scrapped_df.to_html(classes='display table table-striped table-hover" id = "basic-datatables')
        updated_html = html.replace('border="1"', 'border="0"')
        unique_html = updated_html.replace('style="text-align: right;"', '')

        header = "{% extends \"base.html\" %}" + '\n' + \
                 "{% block title %} Tables {% endblock %}" + '\n' + \
                 "{% block stylesheets %}{% endblock stylesheets %}" + '\n' + \
                 "{% block content %}"
        message_start = f"""
                <div class="content">
            		<div class="page-inner">
            			<div class="page-header">
            				<h4 class="page-title">Scraped Reviews Table</h4>
            				<ul class="breadcrumbs">
            					<li class="nav-home">
            						<a href="#">
            							<i class="flaticon-home"></i>
            						</a>
            					</li>
            					<li class="separator">
            						<i class="flaticon-right-arrow"></i>
            					</li>
            					<li class="nav-item">
            						<a href="#">Tables</a>
            					</li>
            					<li class="separator">
            						<i class="flaticon-right-arrow"></i>
            					</li>
            					<li class="nav-item">
            						<a href="#">Scraped Reviews Table</a>
            					</li>
            				</ul>
            			</div>
            			<div class="row">
            				<div class="col-md-12">
            					<div class="card">
            						<div class="card-header">
            							<h4 class="card-title">Reviews Scrpped from provided link Table</h4>
            						</div>
            						<div class="card-body">
            							<div class="table-responsive">
                """
        message_body = unique_html
        message_end = """
                </div>
                						</div>
                					</div>
                				</div>
                			</div>
                		</div>
                	</div>

                {% endblock content %}

                <!-- Specific Page JS goes HERE  -->
                {% block javascripts %}

                	<!-- Atlantis DEMO methods, don't include it in your project! -->
                	<script src="/static/js/setting-demo2.js"></script>
                	<script >
                		$(document).ready(function() {
                			$('#basic-datatables').DataTable({
                			});
                		});
                	</script>

                {% endblock javascripts %}
                """
        messages = (header + message_start + message_body + message_end)

        # print(messages)

        # write html to file
        text_file = open("templates/tables-data.html", "w", encoding='utf-8')
        text_file.write(messages)
        text_file.close()

        df2 = sentiment_pred(scrapped_df)

        return df2


def sentiment_pred(file):
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

        adam = tensorflow.optimizers.Adam(learning_rate=0.0001)
        model.compile(optimizer=adam, loss='binary_crossentropy', metrics=['accuracy'])

        df2 = file  # pd.read_csv('Headphones.csv')
        df2 = df2.drop(columns=['Review Title', 'Rating'])

        x_review = []
        reviews = list(df2['Review'])
        for sen in reviews:
            x_review.append(sen)

        reviews_list_idx = tokenizer.texts_to_sequences(x_review)

        def example(df2, reviews_list_idx):
            df2['sentiment score'] = 0

            reviews_list_idx = pad_sequences(reviews_list_idx, maxlen=172, padding='post')

            review_preds = model.predict(reviews_list_idx)

            df2['sentiment score'] = review_preds
            df2['sentiment score'] = [round(k, 2) for k in df2['sentiment score']]

            pred_sentiment = np.array(list(
                map(lambda x: 'positive' if x > 0.76 else ('neutral' if x <= 0.76 and x >= 0.3 else 'negative'),
                    review_preds)))

            df2['predicted_label'] = 0

            df2['predicted_label'] = pred_sentiment

            return df2

        df2 = example(df2, reviews_list_idx)

        html = df2.to_html(classes='display table table-striped table-hover" id = "basic-datatables')
        updated_html = html.replace('border="1"', 'border="0"')
        unique_html = updated_html.replace('style="text-align: right;"', '')

        header = "{% extends \"base.html\" %}" + '\n' + \
                 "{% block title %} Tables {% endblock %}" + '\n' + \
                 "{% block stylesheets %}{% endblock stylesheets %}" + '\n' + \
                 "{% block content %}"
        message_start = f"""
                        <div class="content">
                    		<div class="page-inner">
                    			<div class="page-header">
                    				<h4 class="page-title">Sentiments Table</h4>
                    				<ul class="breadcrumbs">
                    					<li class="nav-home">
                    						<a href="#">
                    							<i class="flaticon-home"></i>
                    						</a>
                    					</li>
                    					<li class="separator">
                    						<i class="flaticon-right-arrow"></i>
                    					</li>
                    					<li class="nav-item">
                    						<a href="#">Tables</a>
                    					</li>
                    					<li class="separator">
                    						<i class="flaticon-right-arrow"></i>
                    					</li>
                    					<li class="nav-item">
                    						<a href="#">Sentiments Table</a>
                    					</li>
                    				</ul>
                    			</div>
                    			<div class="row">
                    				<div class="col-md-12">
                    					<div class="card">
                    						<div class="card-header">
                    							<h4 class="card-title">Reviews with Sentiments and Score</h4>
                    						</div>
                    						<div class="card-body">
                    							<div class="table-responsive">
                        """
        message_body = unique_html
        message_end = """
                        </div>
                        						</div>
                        					</div>
                        				</div>
                        			</div>
                        		</div>
                        	</div>

                        {% endblock content %}

                        <!-- Specific Page JS goes HERE  -->
                        {% block javascripts %}

                        	<!-- Atlantis DEMO methods, don't include it in your project! -->
                        	<script src="/static/js/setting-demo2.js"></script>
                        	<script >
                        		$(document).ready(function() {
                        			$('#basic-datatables').DataTable({
                        			});
                        		});
                        	</script>

                        {% endblock javascripts %}
                        """
        messages = (header + message_start + message_body + message_end)

        # write html to file
        text_file = open("templates/tables-simple.html", "w", encoding='utf-8')
        text_file.write(messages)
        text_file.close()

        # df2.to_csv('Sentiments of test1.csv', index=True)

        return df2


@app.route('/')
def base():

    return render_template("index.html")


@app.route("/results", methods=["POST"])
def receive_data():
    url = request.form["url"]
    print(url)
    df2 = web_scrap(url)

    if df2 is -1:
        return render_template("error.html")

    dfp = df2[df2.predicted_label == 'positive']
    dfng = df2[df2.predicted_label == 'negative']
    dfn = df2[df2.predicted_label == 'neutral']

    global positive, negative, neutral, pred_pos, pred_neg, pred_neu, ind_p, ind_nt, ind_n, total_reviews
    positive = dfp.shape[0]
    negative = dfng.shape[0]
    neutral = dfn.shape[0]
    total_reviews = df2.shape[0]

    pred_pos = list(dfp['sentiment score'])
    pred_neg = list(dfng['sentiment score'])
    pred_neu = list(dfn['sentiment score'])

    global index
    index = list(df2.index)
    ind_p = list(dfp.index)
    ind_nt = list(dfn.index)
    ind_n = list(dfng.index)

    global sentiment_score, message, index_dash, data_dash
    sentiment_score = list(df2['sentiment score'])

    if total_reviews > 25:
        index_dash = index[0:25]
        data_dash = sentiment_score[0:25]
    else:
        index_dash = index
        data_dash = sentiment_score

    if positive > negative:
        message = 'Your Product is doing Great: Your Positive Review Count is greater than negative Reviews'
    else:
        message = 'Sad! You Need to Work on your Product as : Your Negative Review Count is greater than Positive Reviews'

    dfpr = dfp.sort_values(by=['sentiment score'], ascending=False).head(1)
    global top_pos_cname, top_pos_date, top_pos_rev, icon_pos
    if positive is 0:
        top_pos_cname = "No Positive Review"
        top_pos_date = "N/A"
        top_pos_rev = "N/A"
        icon_pos = "N/A"
    else:
        top_pos_cname = dfpr['Customer Name'].values[0]
        top_pos_date = dfpr['Date'].values[0]
        top_pos_rev = dfpr['Review'].values[0]
        icon_pos = top_pos_cname[0]

    dfnr = dfng.sort_values(by=['sentiment score']).head(1)
    global top_neg_cname, top_neg_date, top_neg_rev, icon_neg
    if negative is 0:
        top_neg_cname = "No Negative Review"
        top_neg_date = "N/A"
        top_neg_rev = "N/A"
        icon_neg = "N/A"
    else:
        top_neg_cname = dfnr['Customer Name'].values[0]
        top_neg_date = dfnr['Date'].values[0]
        top_neg_rev = dfnr['Review'].values[0]
        icon_neg = top_neg_cname[0]

    return render_template("dashboard.html", positive=positive, negative=negative, neutral=neutral,
                           total_reviews=total_reviews, data_dash=data_dash, index_dash=index_dash, message=message,
                           top_pos_rev=top_pos_rev, top_pos_date=top_pos_date, top_pos_cname=top_pos_cname,
                           top_neg_rev=top_neg_rev, top_neg_date=top_neg_date, top_neg_cname=top_neg_cname,
                           icon_neg=icon_neg, icon_pos=icon_pos)


@app.route('/dashboard')
def home():
    return render_template("dashboard.html", positive=positive, negative=negative, neutral=neutral,
                           total_reviews=total_reviews, data_dash=data_dash, index_dash=index_dash, message=message,
                           top_pos_rev=top_pos_rev, top_pos_date=top_pos_date, top_pos_cname=top_pos_cname,
                           top_neg_rev=top_neg_rev, top_neg_date=top_neg_date, top_neg_cname=top_neg_cname,
                           icon_neg=icon_neg, icon_pos=icon_pos)


@app.route('/tables-data')
def datatable():
    return render_template('tables-data.html')


@app.route('/tables-simple')
def simpletable():
    return render_template('tables-simple.html')


@app.route('/charts')
def charts():
    data = sentiment_score
    labels = index
    if total_reviews > 100:
        data = data[0:100]
        labels = labels[0:100]

    pred_labels = [positive, negative, neutral]
    print(ind_p)

    if positive > negative:
        index_2 = ind_p

    elif negative > positive:
        index_2 = ind_n
    else:
        index_2 = ind_nt
    print(data)
    print(labels)
    return render_template('charts.html', data=data, index=labels, sentiments=pred_labels, pred_pos=pred_pos,
                           pred_neg=pred_neg, pred_neu=pred_neu, index_2=index_2)


@app.route('/charts-sparkline')
def sparklinecharts():
    return render_template('charts-sparkline.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
