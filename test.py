import streamlit as st
import mysql.connector as connector
import pandas as pd

con=connector.connect(host='localhost',
                  port='3306',
                  user='root',
                  password='root',
                  database='test')

#print(con)
#query = 'create table if not exists customer(accountnumber number(10) primary key check (accountnumber between 1000000000 and 9999999999), name varchar(25),password varchar(25))'
cur=con.cursor()



def create_custtable():
    cur.execute('create table if not exists customer(accountnumber int primary key check (accountnumber between 1000000000 and 9999999999) , name varchar(25),password varchar(25))')
    con.commit()

#create_custtable()
def create_accttable():
    cur.execute('create table if not exists account(accountnumber int primary key,FOREIGN KEY(accountnumber) REFERENCES customer(accountnumber), balance float DEFAULT 0)')
    con.commit()

def create_trantable():
    cur.execute('create table if not exists transaction(from_acct int, to_acct int, amt float, ts DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)')
    con.commit()

def create_depdrawtable():
    cur.execute('create table if not exists depdraw(accountnumber int, action varchar(15),balance float, ts DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)')
    con.commit()




def add_cust(accountnumber,name,password):
    cur.execute('INSERT INTO customer(accountnumber,name,password) VALUES(%(accountnumber)s,%(name)s,%(password)s)',
                {
        'accountnumber':accountnumber,
        'name':name,
        'password':password,
                })
    cur.execute('INSERT INTO account(accountnumber) VALUES(%(accountnumber)s)',
                {
        'accountnumber':accountnumber,
                })
    con.commit()

def deposit(balance,accountnumber):
    cur.execute('UPDATE account set balance=balance + %(balance)s where accountnumber=%(accountnumber)s',
                {
        'balance':balance,
        'accountnumber':accountnumber,
                })
    create_depdrawtable()
    action='deposit'
    cur.execute('INSERT INTO depdraw(accountnumber,action,balance) VALUES(%(accountnumber)s,%(action)s,%(balance)s)',
                {
        'accountnumber':accountnumber,
        'action':action,
        'balance':balance,
                })
    con.commit()

def witdraw(balance,accountnumber):
    cur.execute('SELECT balance from account where accountnumber=%(accountnumber)s',
                {
        'accountnumber':accountnumber,
                })
    row=cur.fetchone()
    if balance>row[0]:
        st.warning("Insuffient balance, check bal!")
    else:
        cur.execute('UPDATE account set balance=balance - %(balance)s where accountnumber=%(accountnumber)s',
                {
        'balance':balance,
        'accountnumber':accountnumber,
                })
        create_depdrawtable()
        action='withdraw'
        cur.execute('INSERT INTO depdraw(accountnumber,action,balance) VALUES(%(accountnumber)s,%(action)s,%(balance)s)',
                    {
            'accountnumber':accountnumber,
            'action':action,
            'balance':balance,
                    })
        con.commit()
        st.success("success")
        

def showbal(accountnumber):
    cur.execute('SELECT balance from account where accountnumber=%(accountnumber)s',
                {
        'accountnumber':accountnumber,
                })
    
    row=cur.fetchone()
    st.write(row[0])
    con.commit()

def transfer(from_acc,accountnumber,amt):
    cur.execute('SELECT accountnumber from account where accountnumber=%(accountnumber)s',
                {
        'accountnumber':accountnumber,
                })
    
    row = cur.fetchone()
    con.commit()
    if row == None:
        st.warning("Account does not exist")   
    else:
        cur.execute('SELECT balance from account where accountnumber=%(accountnumber)s',
                    {
            'accountnumber':from_acc,
                    })
        row=cur.fetchone()
        #st.write(type(row))
        #st.write(row)
        if amt>row[0]:
            st.warning('Insuffient funds')
        else:
            #st.write('Transaction possible')
            deposit(amt,accountnumber)
            witdraw(amt,from_acc)
            create_trantable()
            cur.execute('INSERT INTO transaction(from_acct,to_acct,amt) VALUES(%(from_acct)s,%(to_acct)s,%(amt)s)',
                {
                'from_acct':from_acc,
                'to_acct':accountnumber,
                'amt':amt,
                })
            st.success('Transfer complete')
            con.commit()

def show_trans(accountnumber):
    cur.execute('SELECT * from transaction where from_acct=%(accountnumber)s',
                {
        'accountnumber':accountnumber,
                })
    data=cur.fetchall()
    return data

def show_depdraw(accountnumber):
    cur.execute('SELECT * from depdraw where accountnumber=%(accountnumber)s',
                {
        'accountnumber':accountnumber,
                })
    data=cur.fetchall()
    return data


def login(accountnumber,Password):
    cur.execute('SELECT accountnumber,password FROM customer WHERE accountnumber=%s AND password =%s',(accountnumber,Password))
    data=cur.fetchall()
    return data

#print("Created")



def main():
    st.title("Online Banking App")

    menu = ["Home","Login","SignUp"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Home":
        st.subheader("Home")
    
    elif choice == "Login":
        st.subheader("Login section")

        accountnumber = st.sidebar.text_input("Acc.no")
        Password = st.sidebar.text_input("Password",type = 'password')
        if st.sidebar.checkbox("Login"):
            create_custtable()
            create_accttable()
            result = login(accountnumber,Password)
            if result:

                st.success("Logged In as {}".format(accountnumber))

                task = st.selectbox("Action",['Deposit','Withdraw','Check Balance','Transfer','Cards','Loan','Transaction History','Withdraw/Deposit History'])
                if task == "Deposit":
                    st.subheader("Deposit money")
                    money = st.number_input("Money",min_value =10.00,max_value=1000000.00)
                    if st.button("deposit"):
                        deposit(money,accountnumber)
                        st.success("money added")

                elif task == "Withdraw":
                    st.subheader("withdraw")
                    money = st.number_input("Money",min_value =10.00,max_value=1000000.00)
                    if st.button("withdraw"):
                        witdraw(money,accountnumber)
                        


                elif task == "Check Balance":
                    st.subheader("Check Balance")
                    if st.button("Check bal"):
                        showbal(accountnumber)

                elif task == "Transfer":
                    st.subheader("Transfer")
                    amt = st.number_input("Money",min_value =10.00,max_value=1000000.00)
                    a_n = st.number_input("Account Number",min_value=1111111111,max_value=9999999999)
                    if st.button("transfer"):
                        transfer(accountnumber,a_n,amt)

                elif task == "Cards":
                    st.subheader("Cards")
                    card=st.selectbox("Type of card",['Credit card','Debit card'])

                    if card == "Credit card":
                        st.subheader("Credit card")

                    elif card == "Debit card":
                        st.subheader("Debit card")

                elif task == "Loan":
                    st.subheader("Loan")

                elif task == "Transaction History":
                    st.subheader("Transaction History")
                    results=show_trans(accountnumber)
                    
                    with st.expander("History"):
                        df=pd.DataFrame(results)
                        st.dataframe(df)

                elif task == "Withdraw/Deposit History":
                    st.subheader("Withdraw/Deposit History")
                    results=show_depdraw(accountnumber)
                    
                    with st.expander("History"):
                        df=pd.DataFrame(results)
                        st.dataframe(df)

            else:
                st.warning("Incorrect Username/Password")
    
    elif choice == "SignUp":
        st.subheader("Create new Account")
        name= st.text_input("Name")
        accountnumber = st.text_input("Phone number")
        password = st.text_input("password",type='password')

        if st.button("SignUp"):
            create_custtable()
            create_accttable()
            add_cust(accountnumber,name,password)
            st.success("You have successfully craeated a valid account")
            st.info("Go to Login Menu to login")




if __name__ == '__main__':
    main()
