import streamlit as st
import requests


API_KEY = 'cur_live_ARnA60CKJUeBudtnf1BtmvvMfm3XcpCaWWaBnw3E'

def convert_currency(amount, curr1, curr2):
    try:
        response = requests.get(
            f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&currencies={curr2}&base_currency={curr1}")
        if response.status_code == 200:
            data = response.json()
            rate = data['data'][curr2]['value']
            converted_amount = round(amount * rate, 2)
            return converted_amount
        else:
            st.write(f"Error: Failed to fetch exchange rates ({response.status_code})")
            return None
    except Exception as e:
        st.write(f"Error: {str(e)}")
        return None

def app():
    st.title("Currency Converter :currency_exchange:")

    # Select Currency and Input Amount
    col1, col2, col3 = st.columns(3)
    with col1:
        curr1 = st.selectbox('Currency 1', ['AED', 'USD', 'PHP', 'EUR'])
    with col2:
        st.markdown("<h1 style='text-align: center; color: grey;'> 🔀 </h1>", unsafe_allow_html=True)
    with col3:
        curr2 = st.selectbox('Currency 2', ['AED', 'USD', 'PHP', 'EUR'])

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Enter the amount to convert:", min_value=0.0, step=1.0)
    with col2:
        if st.button("Convert"):
            result = convert_currency(amount, curr1, curr2)
            if result is not None:
                st.write(
                    f"<h3><span style='color:green'>{amount} {curr1} = {result} {curr2}</span></h3>",
                    unsafe_allow_html=True,
                )

if __name__ == "__main__":
    app()

