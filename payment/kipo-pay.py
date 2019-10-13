from KipoKPG import KipoKPG


"""
    Initial Kipo Library and craete object from KipoKPG class
    Merchant key is merchant phone number
"""
kipo = KipoKPG("YOUR MERCHANT KEY")

"""
    Replace "YOUR CALLBACK URL" and "AMOUNT" with what you want
    kpg_initiate return a Dictionary 
    Successful - {"status": True, "shopping_key": SHOPING_KEY}
    Failed - {"status": false, "message": ERROR_CODE}
"""
kpg_initiate = kipo.kpg_initiate(AMOUNT, 'YOUR CALLBACK URL')

if kpg_initiate['status']:
    """
        Store kpg_initiate["shopping_key"] to session to verfiy
        payment after user came back from gateway

        Call render_form function to render a html form and send
        user to Kipo KPG Gateway (you can create this form manually
        where you want - form example is at the end of Quick Start
    """
    kipo.render_form(kpg_initiate['shopping_key'])
else:
    """
        Show error to user

        You can call getErrorMessage and send error code to that as input
        and get error message
        kipo.get_error_message(ERROR_CODE)
    """
