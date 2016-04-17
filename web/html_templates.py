email_template = """
<h2>Saint A Communications</h2>
<hr>                                            
<p>Hi {leadersname},<br><br>

There is a response to your communication. Details below:<br>

<br><b>Raised by:</b> {leadersname}
<br><b>Raised on:</b> {timestamp}
<br><b>About:</b> {classmembersname}
<br><b>Comment:</b> {comments}
<br>
<br><b>Response from %s:</b> {responses}
<br><br>
<a href='%s' target='_blank'>Click here</a> to submit another communication slip.
<br>
<a href='http://test_responses.stacomms.site/{user_id}' target='_blank'>Click here</a> to access all your communication responses
<br>
<br><i>Thanks.</i>
<br>
<br>
[NB: This is an automated notification email. Do not reply]                
</p>
"""

responses_template = """
<br><b>Raised by:</b> {leadersname}
<br><b>Raised on:</b> {timestamp}
<br><b>About:</b> {classmembersname}
<br><b>Comment:</b> {comments}
<br>
<br><b>Response from %s:</b> {responses}
<br><br>
"""
