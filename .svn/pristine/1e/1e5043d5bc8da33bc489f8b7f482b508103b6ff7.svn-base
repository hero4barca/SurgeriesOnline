from onlinepayment import OnlinePayment,exceptions

class ProcessPayment():

    def __init__(self, cardDetails):
        self.cardDetails = cardDetails

    def process(self):

        auth= { 'username': 'YOUR USERNAME HERE',
        'password': 'YOUR PASSWORD HERE',
        'vendor':   'YOUR VENDOR HERE',
        #'product':  'YOUR PRODUCT HERE' ,
         'partner': 'YOUR PARTNER HERE'}

    # connect to PayPal
        op = OnlinePayment('paypal', test_mode=True, auth=auth)

        # charge a card
        try:
            result = op.sale(first_name = 'Joe',
                             last_name  = 'Example',
                             address    = '100 Example Ln.',
                             city       = 'Exampleville',
                             state      = 'NY',
                             zip        = '10001',
                             amount     = '2.00',
                             card_num   = '4007000000027',
                             exp_date   = '0530',
                             card_code  = '1234')




        except op.TransactionDeclined:
            # do something when the transaction fails
            errorMsg = 'Transaction declined'
            result = None

        except op.CardExpired:
            # tell the user their card is expired
            errorMsg = 'This card has expired'
            result = None

        except op.ProcessorException:
            errorMsg = 'Transaction could not be processed'

            result = None
           # handle all other possible processor-generated exceptions generically


        if not result == None:
            # you can get the raw data returned by the underlying processor too
            orig = result.orig

            # examine result, the values returned here are processor-specific
            success  = result.success
            code     = result.code
            message  = result.message
            trans_id = result.trans_id

        if errorMsg:
            message = errorMsg
        else:
            message = "success:" + str(success) + '\n' + 'code:' + str(code) + '\n' + 'message:' + str(message) + '\n' + 'transaction Id:' + str(trans_id)
            message = message + '/n  +++++++++ /n' + str(orig)

        return message

