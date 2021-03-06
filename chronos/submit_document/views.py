from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import socket
from django.template import Context, Template
from models import User
import utilities
from django.shortcuts import redirect
import json
from django.core.exceptions import ObjectDoesNotExist



#Coinbase API
from coinbase.wallet.client import Client


RECV_HOST = "localhost"
RECV_PORT = 8050
SEND_HOST = "localhost"
SEND_PORT = 7140
SECONDARY_SEND_PORT = 7141


# Create your views here.
@csrf_exempt
def index(request):
	if request.method == 'GET':
		template = loader.get_template('submit_document/index.html')

		ctx = {}	
		ctx["control"] = "GET"
		return HttpResponse(template.render(ctx))

@csrf_exempt
def submit(request):
	if request.method == 'POST':
		#We need use webhooks to check if the coinbase api wallet thingy does shit.
		SANDBOX_URL = 'https://api.sandbox.coinbase.com'
		client = Client(
    		"doxGjrubKnNJ4Y3p",
    		"Bmw4zqIHt3ntIFbRncDHhznfXWGHm24m",
    		base_api_uri=SANDBOX_URL
    	)
		account = client.get_accounts()[0]
		primary_account = client.get_primary_account()
		addr = account.create_address()
		newAddr = addr.address
		btc_address = newAddr
		user_email = request.POST['email']
		hash_value = request.POST['text']
		user = User(email=user_email,
						   btc_address=btc_address,
						   hash_value=hash_value,
						   payment_received=False,
						   txn_hash="null")

		user.save()

		ctx = {}
		ctx['control'] = "POST"
		return redirect('submit_success', address=btc_address)



@csrf_exempt
def submit_success(request, address):
	#print address
	template = loader.get_template('submit_document/submit_success.html')
	#doesn't currently save block information into ctx that the view needs
	ctx = {}
	ctx["addr"]=address
	return HttpResponse(template.render(ctx))


@csrf_exempt
def verify_document(request):
	template = loader.get_template('submit_document/verify_document.html')

	ctx = {}	
	ctx["control"] = "GET"
	return HttpResponse(template.render(ctx))

@csrf_exempt
def document_query(request):
	if request.method == 'POST':
		hash_value = request.POST['text']
		stage_dict={}
		try:
			user = User.objects.get(hash_value=hash_value)
		except ObjectDoesNotExist:
   			stage_dict = {'stage':0}
			return HttpResponse(json.dumps(stage_dict), content_type="application/json")
   		stage = 1
   		if user.payment_received == True:
   			stage = 3
   			stage_dict["txn_hash"]=user.txn_hash
   		#if user.transaction_accepted == True:
   		#	stage = 4
		#TODO:figure out which stage the user as at
		stage_dict['stage']=stage
		return HttpResponse(json.dumps(stage_dict), content_type="application/json")

def about(request):
	template = loader.get_template('submit_document/about.html')
	ctx = {}	
	ctx["control"] = "GET"
	return HttpResponse(template.render(ctx))

