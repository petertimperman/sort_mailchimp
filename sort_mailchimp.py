from mailchimp3 import MailChimp
import pdb 
import shopify
import time 
import os 
from dotenv import load_dotenv, find_dotenv, set_key

if load_dotenv(dotenv_path=find_dotenv()) == False:
	print "Could not find .env file"
	quit()
#KEYS###################
APIKEY= os.getenv("MAIL_CHIMP_KEY")
########################

B2C_AUTO_ID = os.getenv("B2C_AUTO_ID")
B2C_MARINE_ID = os.getenv("B2C_MARINE_ID")



#Authicate shopify
shop_url = os.getenv("SHOP_URL")
shopify.ShopifyResource.set_site(shop_url)
client = MailChimp(mc_api=APIKEY, mc_user='petertimperman')

#Get products and assign type
amount_of_products = shopify.Product.count()
page_size = 250
if page_size >= amount_of_products:
	pages = 1
else:
	pages = amount_of_products / page_size
products = list()
id_type_dict = dict()
for page in range(1, pages+1):
	products += shopify.Product.find(limit=page_size, pag=page)

for product in products:
	#pdb.set_trace()
	if product.product_type == "Marine":
		product_type = "marine"
	elif product.product_type == "Electronics":
		product_type = "both"
	else:
		product_type = "auto"
	id_type_dict[product.id]= product_type

print str(len(id_type_dict)) +" products catogrized"

last_order_date = os.getenv("LAST_ORDER_DATE")
#Get order ids to find customers
amount_of_orders= shopify.Order.count(status="any", created_at_min=last_order_date)
page_size = 250
if page_size >= amount_of_orders:
	pages = 1
else:
	pages = amount_of_orders / page_size

orders = list()
customer_type_dict = dict()
print "Getting %d orders since %s." % (amount_of_orders, last_order_date )
start = time.time()
for page in range(1, pages+1):
	try:
		print page 
		orders += shopify.Order.find(status= "any" ,limit=page_size, page=page, created_at_min=last_order_date)
	except Exception as e:
		print "Orders in the range of "+str(page*page_size) + " to " + str((page+1)*page_size) + "could not be read"
		print e 

end = time.time() - start

set_key(find_dotenv(),"LAST_ORDER_DATE",orders[0].created_at) #Date of the last order set in .env for the next time 
print end 
for order in orders: 
	if order.email != "" and hasattr(order, "customer") and hasattr(order.customer, "accepts_marketing") and  order.customer.accepts_marketing == True:
		customer_type = ""
		for line_item in order.line_items:
			if line_item.product_id is None: #Skip the item if it doesnt have an id  
				without_product_id += 1 
				continue 
			prod_type = id_type_dict[line_item.product_id] 
			if customer_type != "both" and customer_type != "" and customer_type != prod_type:
				customer_type = "both"
			else:
				customer_type = prod_type
		if order.email in customer_type_dict:
			if customer_type_dict[order.email] != "both" and customer_type_dict[order.email] != customer_type:
				customer_type_dict[order.email] = "both"
		else:
			customer_type_dict[order.email] = customer_type

for customer_email in customer_type_dict.keys():
	print customer_email
	print customer_type_dict[customer_email]
	if customer_type_dict[customer_email] == "auto":
		try:
			client.lists.members.create(B2C_AUTO_ID, {
			    'email_address': customer_email,
			    'status': 'subscribed',
			   
			})
		except Exception as e:

			print "Already in atuo"
	elif customer_type_dict[customer_email] == "marine":
		try:
			client.lists.members.create(B2C_MARINE_ID, {
			    'email_address': customer_email,
			    'status': 'subscribed',
			   
			})
		except Exception as e:
			print "Already in marine"
	else:
		try:
			client.lists.members.create(B2C_AUTO_ID, {
			    'email_address': customer_email,
			    'status': 'subscribed',
			   
			})
			client.lists.members.create(B2C_MARINE_ID, {
			    'email_address': customer_email,
			    'status': 'subscribed',
			  
			})
		except Exception as e:
			print "Already in both"
	

		 



































