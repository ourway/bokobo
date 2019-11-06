import time
import json
import requests
import webbrowser


class KipoKPG:
    merchant_key = ''

    __shopping_key = ''
    __referent_code = ''

    """
        Default headers
        don't change default values

        :var array
    """
    __headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    """
        Default post data parameters and keys
        :var array
    """
    __post_data = {}

    """
        Contain error code explanation
        :var array
    """
    ERROR_MESSAGE = {
        -1: ".خطایی در داده‌های ارسالی وجود دارد،‌ لطفا اطلاعات را بررسی کنید و دوباره ارسال نمایید. (درخواست پرداخت)",
        -2: "خطایی در تحلیل داده‌های در سرور کیپو بوجود آمده است، دقایقی دیگر امتحان فرمایید.",
        -3: "امکان برقراری ارتباط با سرور کیپو میسر نمی‌باشد.",
        -4: "خطایی در داده‌های ارسالی وجود دارد،"
            "‌ لطفا اطلاعات را بررسی کنید و دوباره ارسال نمایید. (بررسی تایید پرداخت)",
        -5: "پرداخت توسط کاربر لغو شده یا با مشکل مواجه شده است",
        -6: "شماره تماس فروشنده مورد نظر مورد تایید نمی‌باشد.",
        -7: "حداقل مبلغ پرداخت 1,000 ریال می‌باشد.",
        -8: "حداکثر مبلغ پرداخت 30,0000,000 ریال می‌باشد.",
        -9: "شناسه پرداخت ارسالی مورد تایید نمی‌باشد."
    }

    """
    API Action urls
    """
    API_GENERATE_TOKEN = 'api/v1/token/generate'
    API_VERIFY_TOKEN = 'api/v1/payment/verify'

    """
        Kipo server application url
        :var array
    """

    kipo_webgate_url = "http://webgate.kipopay.com/"

    def __init__(self, merchant_key):
        if merchant_key:
            self.merchant_key = merchant_key

    """
        Get two parameter for amount and call back url and send data
        to kipo server, retrieve shopping key to start payment, after
        shopping key received, render form must be called or create form
        manually

        :param amount
        :param callback_url
        :return dict
    """

    def kpg_initiate(self, amount, callback_url):
        self.__post_data = {
            "merchant_mobile": self.merchant_key,
            "payment_amount": amount,
            "callback_url": callback_url
        }

        s = requests.Session()
        req = requests.Request('POST',
                               self.kipo_webgate_url + self.API_GENERATE_TOKEN,
                               data=json.dumps(self.__post_data),
                               headers=self.__headers)
        prepped = req.prepare()

        try:
            resp = s.send(prepped,
                          verify=False,
                          cert=False,
                          timeout=10000,
                          )
        except:
            return {
                "status": False,
                "code": -3,
                "message": self.get_error_message(-3),
            }

        response = json.loads(resp.text)

        if resp.status_code == 200:
            shopping_key = response['payment_token']
            self.__shopping_key = shopping_key

            return {
                "status": True,
                "shopping_key": shopping_key
            }

        else:
            return {
                "status": False,
                "code": -1,
                "message": self.get_error_message(-1),
            }

    """
        Send inquery request to kipo server and retrieve
        payment status, if response contain ReferingID, that
        payment was successfully

        :param shopping_key
        :return dict
    """

    def kpg_inquery(self, shopping_key):
        self.__post_data = {
            "payment_token": shopping_key
        }

        s = requests.Session()
        req = requests.Request('POST',
                               self.kipo_webgate_url + self.API_VERIFY_TOKEN,
                               data=json.dumps(self.__post_data),
                               headers=self.__headers)
        prepped = req.prepare()

        try:
            resp = s.send(prepped,
                          verify=False,
                          cert=False,
                          timeout=10000,
                          )
        except:
            return {
                "status": False,
                "code": -3,
                "message": self.get_error_message(-3),
            }

        response = json.loads(resp.text)

        if resp.status_code == 200:

            if 'referent_code' in response:
                self.__referent_code = response['referent_code']

                return {
                    "status": True,
                    "referent_code": self.__referent_code,
                    "amount": response['payment_amount']
                }

            return {
                "status": False,
                "code": -5,
                "message": self.get_error_message(-5)
            }

        else:
            return {
                "status": False,
                "code": -4,
                "message": self.get_error_message(-4)
            }

    """
        This function render a simple form to
        redirect user to kipo webgate with shopping key

        :param shopping_key
    """

    def render_form(self, shopping_key):
        f = open('form.html', 'w')
        html_form = """
            <form id="kipopay-gateway" method="post" action="{url}" style="display: none;">
                <input type="hidden" id="sk" name="sk" value="{shopping_key}"/>
            </form>
        <script language="javascript">document.forms['kipopay-gateway'].submit();</script>
        """.format(url=self.kipo_webgate_url, shopping_key=shopping_key)

        f.write(html_form)
        f.close()

        webbrowser.open_new_tab("form.html")

    """
        Retrieve to user shopping key property

        :return str
    """

    def get_shopping_key(self):
        return self.__shopping_key

    """
        Retrieve to user shopping key property

        :return str
    """

    def get_referent_code(self):
        return self.__referent_code

    """
        Retrieve error message

        :param error_code
        :return mixed|None
    """

    def get_error_message(self, error_code):
        return_error = None

        if isinstance(error_code, int):
            return_error = self.ERROR_MESSAGE[error_code]

        return return_error