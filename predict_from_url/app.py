from flask import Flask, render_template,request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.models import model_from_json


# load json and create model
json_file = open('./model/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json, custom_objects={"KerasLayer": hub.KerasLayer})
# load weights into new model
model.load_weights("./model/model.h5")



app = Flask(__name__)



def get_tweet_txt(url):
    path = "./chromedriver/chromedriver.exe"
    driver = webdriver.Chrome(path)
    driver.get(url)
    time.sleep(10)
    close_notif_button = driver.find_element('xpath','//div[@role="button"]')
    close_notif_button.click()
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//article[@role='article']")))
    user = element.find_element('xpath',".//span[contains(text(), '@')]").text
    text = element.find_element('xpath','.//div[@lang]').text
    driver.quit()
    return user, text


def pred_url(url, model=model):
    user, tweet = get_tweet_txt(url)
    pred = round(model.predict([tweet])[0][0])
    return pred


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        user, text = get_tweet_txt(url)
        if pred_url(url):
            sino = ''
        else:
            sino = "N'T"
        try:
            return f'''
                <div>
                    <p>The tweet: </p>
                    <p>{text}</p>
                    <p>From the user:</p>
                    <p>{user}</p>
                    <p>IS{sino} about a disaster or a catastrophe.</p>
                </div>

                <p>Evaluate another tweet</p>
                <form method='POST'>
                    <input type="text" name="url">
                    <input type="submit" value="Evaluate tweet"/>
                </form>
                <form action="/">
                    <input type="submit" value="Volver">
                </form>'''
        except:
            return "Error. Try again later."

    return f'''
                <p>Insert a tweet's URL to see if it's a disaster or not.</p>
                <form method='POST'>
                    <input type="text" name="url">
                    <input type="submit" value="Evaluate tweet"/>
                </form>
                <form action="/">
                    <input type="submit" value="Volver">
                </form>
            '''




if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0')


