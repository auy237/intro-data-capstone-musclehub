
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL


# In[28]:

# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query

# In[31]:

# Examine visits here
sql_query('''
select*
from visits
limit 5''')


# In[32]:

# Examine fitness_tests here
sql_query('''
select*
from fitness_tests
limit 5''')


# In[33]:

# Examine applications here
sql_query('''
select*
from applications
limit 5''')


# In[34]:

# Examine purchases here
sql_query('''
select*
from purchases
limit 5''')

# In[35]:

#SQL code for MuscleHub
df = sql_query('''
SELECT
    visits.first_name,
    visits.last_name,
    visits.gender,
    visits.email,
    visits.visit_date,
    fitness_tests.fitness_test_date,
    applications.application_date,
    purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON fitness_tests.first_name = visits.first_name 
    AND fitness_tests.last_name = visits.last_name 
    AND fitness_tests.email = visits.email
LEFT JOIN applications
    ON applications.first_name = visits.first_name 
    AND applications.last_name = visits.last_name 
    AND applications.email = visits.email
LEFT JOIN purchases
    ON purchases.first_name = visits.first_name 
    AND purchases.last_name = visits.last_name 
    AND purchases.email = visits.email
WHERE visits.visit_date >= '7-1-17'
''')

df[0:5]


# ## Step 3: Investigate the A and B groups

# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[36]:

import pandas as pd
from matplotlib import pyplot as plt


# add some columns to `df` to help us with analysis.
# 
# add a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[37]:

#new column for A/B test
df["ab_test_group"] = df.fitness_test_date.apply(lambda x: "A"                                        if pd.notnull(x) else "B")
df[0:5]


# In[38]:

#A/B grouping 
ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()


# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[39]:

#pie plot 
plt.pie(ab_counts.first_name.values,labels=['A','B'],autopct = '%0.2f%%')
plt.axis('equal')
plt.show()
plt.savefig('ab_test_pie_chart.png')


# ## Step 4: Who picks up an application?

# sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 

# In[40]:

# new column for application check
df['is_application'] = df.application_date.apply(lambda x: 'Application' if pd.notnull(x) else 'No Application')


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[41]:

#group application check
app_counts = df.groupby(['ab_test_group','is_application']).first_name.count().reset_index()
app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[42]:

#pivot application
app_pivot = app_counts.pivot(columns='is_application',index='ab_test_group',values='first_name').reset_index()
app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[43]:

#add column 'Total'
app_pivot['Total'] = app_pivot['Application'] + app_pivot['No Application']
app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[44]:

#add column 'Percent with Application'
app_pivot['Percent with Application'] = app_pivot['Application'] / app_pivot['Total']
app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[45]:

from scipy.stats import chi2_contingency

#list of each test group
x = [[250, 2254],[325,2175]]
chi2,pval,dof,expected = chi2_contingency(x)
pval


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[46]:

#add column check for Membership
df['is_member'] = df.purchase_date.apply(lambda x: 'Member' if pd.notnull(x) else 'Not Member')


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[47]:

#filter df for just applications
just_apps = df[df.is_application == 'Application']


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[48]:

#new dataframe for just applications
group_member = just_apps.groupby(['is_member','ab_test_group']).first_name.count().reset_index()
member_pivot = group_member.pivot(columns='is_member',index='ab_test_group',values='first_name').reset_index()
member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot['Member'] / member_pivot['Total']
member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[49]:

#list of each test group
y = [[200, 50],[250,75]]
chi2,pval,dof,expected = chi2_contingency(y)
pval


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[50]:

# dataframe for all visitors purchasing memberships
final_group_member = df.groupby(['is_member','ab_test_group']).first_name.count().reset_index()
final_member_pivot = final_group_member.pivot(columns='is_member',index='ab_test_group',values='first_name').reset_index()
final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot['Member'] / final_member_pivot['Total']
final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[51]:

#list of each test group
z = [[200, 2304],[250,2250]]
chi2,pval,dof,expected = chi2_contingency(z)
pval


# In[52]:

## Step 5: Summarize the acquisition funel with a chart


# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[57]:

#visitors applying chart
ax = plt.subplot()
plt.bar(range(len(app_pivot)),app_pivot['Percent with Application'].values)
plt.title('Percent with Application')
vals = ax.get_yticks()
ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
plt.show()
plt.savefig('visitors_applying.png')


# In[54]:

#applicants buying a membership
ax = plt.subplot()
plt.bar(range(len(app_pivot)),member_pivot['Percent Purchase'].values)
plt.title('Application w/ Membership')
vals = ax.get_yticks()
ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
plt.show()
plt.savefig('members_applying.png')


# In[56]:

#visitors buying a membership
ax = plt.subplot()
plt.bar(range(len(app_pivot)),final_member_pivot['Percent Purchase'].values)
plt.title('Visitors buying Membership')
vals = ax.get_yticks()
ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
plt.show()
plt.savefig('visitors_applying_purchase.png')


# In[ ]:



