from flask import Flask , render_template, url_for, request, session, make_response, redirect
import json
import csv
import tensorflow as tflow
import nltk
from nltk.stem.lancaster import LancasterStemmer
import pickle
import json
import random
import time
import numpy as np
from keras.models import load_model
from flask import jsonify


app = Flask(__name__)
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/shop2')
def shop2():
    return render_template('shop2.html')

@app.route('/shop3')
def shop3():
    return render_template('shop3.html')

@app.route('/shop4')
def shop4():
    return render_template('shop4.html')

@app.route('/shop5')
def shop5():
    return render_template('shop5.html')

@app.route('/shop6')
def shop6():
    return render_template('shop6.html')

@app.route('/sproduct')
def sproduct():
    image = request.args.get('image')
    name = request.args.get('name')
    price = request.args.get('price')
    return render_template('sproduct.html', image=image, name=name, price=price)

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    # print(cart)
    cart_total=0
    # cart_total = sum(item['discount_price'] * item['quantity'] for item in cart)
    for item in cart:
        if item['discount_price']==0:
            cart_total+=(item['price']*item['quantity'])
        else: cart_total+=(item['discount_price']*item['quantity'])
    return render_template('cart.html', cart=cart, cart_total=cart_total)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    name = data.get('name')
    size = data.get('size')
    quantity = data.get('quantity')
    price = data.get('price')
    image = data.get('image')
    image1=image.replace('http://127.0.0.1:5000','..')
    image_to_product = {}
    with open('image_to_product.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            image_to_product[row['image']] = row['product_id']
    product_id = image_to_product.get(image1)
    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = int(item['quantity'])+int(quantity)
            session['cart'] = cart
            return render_template('cart.html')
    cart_item = {
        'product_id': product_id,
        'name': name,
        'size': size,
        'quantity': int(quantity),
        'price': int(price),
        'image': image,
        'discount_price': session.get('discount_price')
    }
    # print("-------")
    # print(cart_item['discount_price'])
    cart.append(cart_item)
    session['cart'] = cart
    session['discount_price']=0
    return render_template('cart.html')

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    cart = session.get('cart', [])
    # print(cart)
    # print(product_id)
    # updated_cart = [item for item in cart if item['product_id'] != product_id]
    updated_cart=[]
    for item in cart:
        if int(item['product_id'])!=int(product_id):
            updated_cart.append(item)
    session['cart'] = updated_cart
    # print(session['cart'])
    return render_template('cart.html')

graph = tflow.Graph()
stemmer = LancasterStemmer()

data = pickle.load( open("chatbot//training_data", "rb") )
words = data['words']
documents = data['documents']
classes = data['classes']

with open('chatbot//intent.json') as json_data:
    intents = json.load(json_data)

model = load_model('chatbot//chatmodel.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))

context = {}

ERROR_THRESHOLD = 0.50
def classify(sentence):
    p = bow(sentence, words)
    d = len(p)
    f = len(documents)-2
    a = np.zeros([f, d])
    tot = np.vstack((p, a))
    results = model.predict(tot)[0]
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
    # print(results)
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # print(return_list)
    return return_list

user_offer_count = 1
bot_offer_count = 0

def extract_amount(sentence): 
    try:
        sentence = sentence.lower()
        if "rs." in sentence:
            price_start = str.find(sentence, "rs.") # store the index of 'Rs.'
            price_end = str.find(sentence, "/-") # store the index of '/-'
            amount = sentence[price_start+3:price_end] # extract the amount
            amount = amount.strip() # remove spaces
            return int(amount)
        else: return None
    except:
        return 'invalid_amount'
    
def track_user_offer(userText):
    userText = userText.lower()
    if 'rs.' in userText:
        global user_offer_count
        user_offer_count += 1
    return user_offer_count

def track_bot_offers():
    global bot_offer_count
    bot_offer_count += 1
    return bot_offer_count

def create_offer(min_acceptable_price,original_price,bot_offer_count,user_offer,give_offer=False): 
    discount_percentage = int(((original_price - min_acceptable_price)/original_price) * 100)
    percentage_per_step = (discount_percentage / 4)
    app.logger.info(give_offer)
    if give_offer:
        # first offer
        if bot_offer_count == 1:
            # print(percentage_per_step)
            app.logger.info('bot offer 1 is executing')
            discounted_amount = (original_price/100) * (percentage_per_step*1)
            # print(discounted_amount)
            bot_offer = original_price - discounted_amount
            # print(round(int(bot_offer), -2))
            return round(bot_offer)
        # 2nd offer
        elif bot_offer_count == 2:
            app.logger.info('bot offer 2 is executing')
            discounted_amount = (original_price/100) * (percentage_per_step*2)
            bot_offer = original_price - discounted_amount
            app.logger.info(bot_offer)
            return round(bot_offer)
        # 3rd offer
        elif bot_offer_count == 3:
            app.logger.info('bot offer 3 is executing')
            discounted_amount = (original_price/100) * (percentage_per_step*3)
            bot_offer = original_price - discounted_amount
            return round(bot_offer)
        # last full and final offer
        else:
            app.logger.info('bot offer final is executing')
            discounted_amount = (original_price/100) * (percentage_per_step*4)
            bot_offer = original_price - discounted_amount
            return round(bot_offer)
        
def response(sentence, userID, min_acceptable_price,user_offer, original_price, show_details=False):
    global bot_offer_count
    results = classify(sentence)
    print('Result:', results)
    if extract_amount(sentence)!=None:
        # print("hey")
        if ((user_offer >= min_acceptable_price) and (user_offer <= original_price)):
            accept_response = 'suitable offer by the customer'
            session['bot_offer']=user_offer
            return accept_response
        elif user_offer > original_price or user_offer == 0:
            response = 'foolish offer'
            return response
        elif user_offer < min_acceptable_price:
            bot_offer_count = track_bot_offers()
            # app.logger.info(bot_offer_count)
            bot_offer = create_offer(min_acceptable_price, original_price, bot_offer_count,user_offer,True)
            print('bot offer : ',bot_offer)
            session['bot_offer'] = bot_offer
            print(session['bot_offer'])
            intents['intents'][10]['tag'] = 'customeroffers'
            res = random.choice(intents['intents'][10]['responses'])
            # print('Intents:', intents['intents'][10])
            if bot_offer_count > 3:
                response = "final offer+" + str(bot_offer)
                return response 
            if '___' in res:
                res = res.replace('___', str(bot_offer))
            return res
    if results:
        print("hello")
        while results:
            for i in intents['intents']:
                if i['tag'] == results[0][0]:
                    print(results[0][0])
                    if 'context_set' in i:
                        if show_details: print('context: ', i['context_set'])
                        context[userID] = i['context_set']
                    if not 'context_filter' in i:
                        print("here iam")
                        # if show_details: print('tag:', i['tag'])  
                        if i['tag'] == 'customeroffers' or i['tag']=='finaloffer':
                            if ((user_offer >= min_acceptable_price) and (user_offer <= original_price)):
                                accept_response = 'suitable offer by the customer'
                                session['bot_offer']=user_offer
                                return accept_response
                            elif user_offer > original_price or user_offer == 0:
                                response = 'foolish offer'
                                return response
                            elif user_offer < min_acceptable_price:
                                bot_offer_count = track_bot_offers()
                                app.logger.info(bot_offer_count)
                                bot_offer = create_offer(min_acceptable_price, original_price, bot_offer_count,user_offer,True)
                                print("crossed cerate_offer")
                                session['bot_offer'] = bot_offer
                                res = random.choice(i['responses'])
                                if bot_offer_count > 3:
                                    response = "final offer+" + str(bot_offer)
                                    return response 

                                if '___' in res:
                                    res = res.replace('___', str(bot_offer))
                                    return res
                        elif i['tag']=='acceptcustomeroffer':
                            bot_offer_count=0
                            print("gng in")
                            session['discount_price'] = session['bot_offer']
                            print("hee")
                            print(session['discount_price'])
                            return random.choice(i['responses'])
                        elif i['tag']=='deal':
                            bot_offer_count=0
                            print("im in deal")
                            # print(session['bot_offer'])
                            session['discount_price']=session['bot_offer']
                            return random.choice(i['responses'])
                        else: return random.choice(i['responses'])

            results.pop(0)


@app.route('/get_bot_response', methods=['POST'])
def get_bot_response():
    userText = request.json['message']
    user_offer = extract_amount(userText)
    original_price = request.json['price']
    original_price = int(original_price)
    min_acceptable_price = original_price - ((original_price * 20) / 100)
    print(min_acceptable_price)
    # print(user_offer)
    time.sleep(0.5)
    try: 
        res = response(userText, '123', min_acceptable_price, user_offer, original_price)
        # print(res)
        if user_offer == 'invalid_amount':
            res = response("bla bla", '123', min_acceptable_price, user_offer, original_price)
        elif res == 'suitable offer by the customer':
            accept_response = 'suitable offer by the customer'
            res = response(accept_response, '123', min_acceptable_price, user_offer, original_price)
            if '___' in res:
                print("yes")
                res = res.replace('___', str(user_offer))
            if 'discount_price' not in session:
                session['discount_price'] = user_offer
            print("final price here")
            print(session['discount_price'])
        elif res == 'foolish offer':
            deny_foolish_offer = res
            res = response(deny_foolish_offer, '123', min_acceptable_price, user_offer, original_price)
        elif 'final offer' in res:
            print("im in final offer")
            res_split = res.split('+')
            final_offer = res_split[1]
            print(res_split[0])
            res = response(res_split[0], '123', min_acceptable_price, user_offer, original_price)
            if '___' in res:
                res = res.replace('___', str(final_offer))
    except Exception as e:
        print(f"An error occurred while processing the request: {e}")
        # res = "Oops! Something went wrong. Please try again later."
        res = response("bla bla", '123', min_acceptable_price, user_offer, original_price)  

    return jsonify({'bot_response': res})



      
if __name__ == "__main__":
    app.run(debug=True)