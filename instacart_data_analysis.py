import pandas as pd
import matplotlib.pyplot as plt
import re
import seaborn as sb
import numpy as np


    #data import

o = pd.read_csv('orders.csv')
p = pd.read_csv('products.csv')
op = pd.read_csv('order_products__test.csv')
d = pd.read_csv('departments.csv')
a = pd.read_csv('aisles.csv')
o['days_since_prior_order'] = o['days_since_prior_order'].fillna(0)



    ## In what time of day are specific products most frequently ordered?

temp=pd.merge(o,op,on='order_id')
temp2=pd.merge(temp,p,on='product_id')
del(temp)

temp2.groupby('order_hour_of_day',as_index=False).agg({'order_id': ['count']}).plot(kind='bar')


    ## On what day of week are specific products most frequently ordered?
    
temp=pd.merge(o,op,on='order_id')
temp2=pd.merge(temp,p,on='product_id')
temp2_agg = temp2.groupby('order_dow',as_index=False).agg({'order_id': ['count']})

temp_plot = plt.bar(temp2_agg[('order_dow',      '')],temp2_agg[( 'order_id', 'count')])

sum_height = 0.0
for bar in temp_plot: sum_height += bar.get_height()

for bar in temp_plot:
    percentage = bar.get_height()/sum_height
    plt.annotate( f"{percentage:.2%}",(bar.get_x() + bar.get_width()/2, bar.get_height()+.05),ha="center",va="bottom",fontsize=7)

plt.show()


# what does the 0 represent? Sunday?(most likely) Monday? Or N/A?



    ## Which department has the most order count?

temp=pd.merge(op,p,on='product_id')
temp3 = temp.groupby('department_id', as_index=False).agg({'order_id': ['count']})
del temp
temp3 = pd.merge(temp3, d, on='department_id') #why is there system message "FutureWarning: merging between different levels is deprecated and will be removed in a future version. (2 levels on the left, 1 on the right)"
del temp3['department_id'] ; del temp3[('department_id', '')]
temp3 = temp3.sort_values(by=[('order_id', 'count')],ignore_index=True, ascending=False)
temp3 = temp3.drop(index=[15,17],axis=0)

plt.figure(figsize=(25,5))
plt.bar(temp3['department'].values, temp3[('order_id', 'count')].values, width=0.3)
plt.ylabel('order count')
plt.title('Order count by department')
plt.xticks(rotation = 30)  
plt.show()


plt.figure(figsize=(25,5))
plt.bar(temp3['department'].values, temp3[('order_id', 'count')].values, width=0.3)
plt.ylabel('log of order count')
plt.title('Order count by department (log scale)')
plt.yscale('log')
plt.xticks(rotation = 30)  
plt.show()

    ## Which aisles have the most order count?
    
#first, clear out all bad code in 'aisles.csv'

a = pd.read_csv('aisles.csv')
cleared_strings=[]

for i in range(len(a)): cleared_strings.append(' '.join( re.findall('[A-Za-z]+', a['aisle'][i]) ))
temp=pd.DataFrame({'aisle_cleared': pd.Series(cleared_strings)})
a=pd.concat([a,temp],axis=1)
a['aisle_id'][243]=9  # the aisle ID of 9 is missing, but there is an aisle which has no ID, assign 9 to it.

#created a column named 'aisle_cleared' as the cleared-out result

temp=pd.merge(o,op, on='order_id')
temp=pd.merge(temp,p, on='product_id')
temp=pd.merge(temp,a,on='aisle_id')

temp_agg=temp.groupby('aisle_cleared',as_index=False).agg({'order_id': ['count']})
temp_agg.plot(kind='bar')

# Observations indicate that the top 10 aisles have the most orders
temp_agg['rank'] = temp_agg[(     'order_id', 'count')].rank(ascending=False, method='min')
temp_agg=temp_agg.sort_values(by=['rank'],ignore_index=True)

temp_agg.head(10).to_excel('temp.xlsx')


plt.yscale('linear')
plt.title('linear scale of order count by aisle')
plt.ylabel('order count')
plt.bar(temp_agg[('aisle_cleared',      '')],temp_agg[(     'order_id', 'count')])

plt.yscale('log')
plt.title('logarithmic scale of order count by aisle')
plt.ylabel('order count')
plt.bar(temp_agg[('aisle_cleared',      '')],temp_agg[(     'order_id', 'count')]) #but how to get rid of all the aisle names that pile up together into a mess?

# .axes.get_xaxis().set_visible(False)

    ## Who are the loyal customers?

    # What is the distribution of customer order volumes?

temp=o.groupby('user_id', as_index=False).agg({'order_id': ['count']})
temp['rank']=temp[('order_id', 'count')].rank(ascending=False, method='min')
temp=temp.sort_values(by=['rank'],ignore_index=True)
temp2=temp.groupby(('order_id', 'count'),as_index=False).agg({'count'})

plt.bar( temp2.index, temp2[('user_id', '', 'count')].values )
plt.xlabel('total purchases')
plt.ylabel('customer count')
plt.title('distribution of customers\' total purchases')
plt.yscale('linear')
plt.show()

# cumulative purchases graph
total = 0; totals=[]
for i in range(len(temp2.index)):
    total += temp2.index[i] * temp2[('user_id', '', 'count')].values[i]
    totals.append(total)
totals = [totals[i]/total for i in range(len(totals))]
plt.bar( temp2.index, totals )
plt.xlabel('total purchases')
plt.ylabel('customer percentage (cumulative)')
plt.title('cumulative percentage of customers\' total purchases')
plt.yscale('linear')
plt.show()

# log scale graph
plt.bar( temp2.index, temp2[('user_id', '', 'count')].values )
plt.yscale('log')
plt.show()

# The log-scale of customer density distribution is negatively-linear related to order-count,
# with a notable exception at order-count = 100, with more than expected numbers of customers

def percentile(input_list, index): 
    'calculate the percentile of the sum of all numbers before the index (index EXCLUDED)!'
    temp_sum=0
    for i in range(index): temp_sum += input_list[i]
    return temp_sum/sum(input_list)

percentile(temp2[('user_id', '', 'count')].values, 48)  
    # ~=95%, indicating that customers who made over 50 orders are among the top 5% loyal customers
percentile(temp2[('user_id', '', 'count')].values, 34)
    # ~=90%, indicating that customers who made over 35 orders are among the top 10% loyal customers
percentile(temp2[('user_id', '', 'count')].values, 21)
    # ~=80%, indicating that customers who made over 23 orders are among the top 20% loyal customers



    # weird department names


temp=pd.merge(op,p,on='product_id')
temp3 = temp.groupby('department_id', as_index=False).agg({'order_id': ['count']})
del temp
temp3 = pd.merge(temp3, d, on='department_id') #why is there system message "FutureWarning: merging between different levels is deprecated and will be removed in a future version. (2 levels on the left, 1 on the right)"
del temp3[('department_id', '')] ; # del temp3['department_id'] ;
temp3 = temp3.sort_values(by=[('order_id', 'count')],ignore_index=True, ascending=False)

# "nuclear missles" (id: 18, same with "babies"); 
# "illegal drugs" (id: 6, same with "international")
# "missing" (id: 21)

nuclear = p[p['department_id']==18]
drugs = p[p['department_id']==6]
missing = p[p['department_id']==21]

def all_words(list_in):
    'return all separate english words in the list, repeats are ignored'
    list_out = list()
    for elem in list_in: 
        list_temp = re.findall('[A-Za-z]+', elem)
        for e in list_temp:  list_out.append(e)
    return sorted(list(set(list_out)))

nuclear_words = all_words(nuclear['product_name'])
drugs_words = all_words(drugs['product_name'])
missing_words = all_words(missing['product_name'])



# no words related to nuclear missles or illegal drugs are detected in the two rows

# the sales and ID of "nuclear missles" are close to "babies", and "illegal drugs" close to "international";

# the "missing" department contains a variety of groceries from other department, further sorting may be needed



    # Which products are most frequently purchased?

# frequency of product occurance in orders (multiples of the same item are not included)

temp = pd.merge(op,p,on='product_id')
temp_agg = temp.groupby('product_name',as_index=False).agg({'product_id': ['count']})
temp_agg=temp_agg.sort_values(by=[('product_id', 'count')],ignore_index=True, ascending=False)

temp_agg.head(30).to_excel('temp.xlsx')

# frequency of product true order counts (considering multiples of the same item in one order)

temp = pd.merge(op,p,on='product_id')
temp_agg = temp.groupby('product_name',as_index=False).agg({'add_to_cart_order': ['sum']})
temp_agg=temp_agg.sort_values(by=[('add_to_cart_order', 'sum')],ignore_index=True, ascending=False)

temp_agg.head(30).to_excel('temp.xlsx')



    # Heat map of Day of week by Hour of day
    
# creating a 2-Dimensional dataframe of day_of_week and hour_of_day

days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
list_temp = list()
dict_temp = dict()
for i in range(len(days)):
    list_temp = list()
    for j in range(24):
        list_temp.append( len(o[ o['order_hour_of_day'] == j][ o['order_dow'] == i ]) )
    dict_temp.update( {days[i]:list_temp} )

heat_data = pd.DataFrame(dict_temp)

ax = sb.heatmap(heat_data)


    # sell of organic food V.S. inorganic food
    

temp = pd.merge(op,p,on='product_id')
temp_agg = temp.groupby('product_name',as_index=False).agg({'add_to_cart_order': ['sum']})
temp_agg=temp_agg.sort_values(by=[('add_to_cart_order', 'sum')],ignore_index=True, ascending=False)


sales_organic = pd.DataFrame()
sales_inorganic = pd.DataFrame()

for i in range(len(temp_agg)):
    if bool(re.findall('[Oo]rganic',temp_agg[(     'product_name',    '')][i])) == True:
        sales_organic = pd.concat([sales_organic,temp_agg.iloc[i:(i+1)]],ignore_index = True)
    else:
        sales_inorganic = pd.concat([sales_inorganic,temp_agg.iloc[i:(i+1)]],ignore_index = True)


    # Days since prior order distribution

temp2 = o[ o['days_since_prior_order'] == o['days_since_prior_order'] ] # filter out the NaN values
temp2_agg = temp2.groupby('days_since_prior_order',as_index=False).agg({'order_id': ['count']})
temp2_agg = temp2_agg.sort_values(by=['days_since_prior_order'],ignore_index=True, ascending=False)

temp2_agg = temp2_agg.sort_values(by=[(              'order_id', 'count')],ignore_index=True, ascending = False)

plt.bar( temp2_agg[('days_since_prior_order',      '')],temp2_agg[(              'order_id', 'count')] )
plt.xlabel('days since prior order')
plt.ylabel('number of customers')
plt.title('distribution of customers\' days since prior order')
plt.show()




