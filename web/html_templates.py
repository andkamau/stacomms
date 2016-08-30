email_template = """
<h2>Westi YA Communications</h2>
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
<a href='%s/{user_id}' target='_blank'>Click here</a> to access all your communication responses
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
<br><b>Communication raised:</b> {comments}
<br>
<br><b>Response from %s:</b> {responses}
<br><br>
"""

_responses_template = """
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>Westi YA Communications</title>
  <meta name="description" content="Westi YA digital communications platform">

  <link rel="stylesheet" href="http://stacomms-test.s3-website.eu-central-1.amazonaws.com/css/main.css">
  <link rel="canonical" href="http://westiyacomms.site/index.html">
  <link rel="alternate" type="application/rss+xml" title="Westi YA Communications" href="http://westiyacomms.site/feed.xml">

  <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
  <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
</head>

<body>
 
 <header class="site-header">

  <div class="wrapper">

      <a class="site-title" href="http://westiyacomms.site/"><p>Westi YA Communications</p></a>

    <nav class="site-nav">
      <a href="#" class="menu-icon">
        <svg viewBox="0 0 18 15">
          <path fill="#424242" d="M18,1.484c0,0.82-0.665,1.484-1.484,1.484H1.484C0.665,2.969,0,2.304,0,1.484l0,0C0,0.665,0.665,0,1.484,0 h15.031C17.335,0,18,0.665,18,1.484L18,1.484z"/>
          <path fill="#424242" d="M18,7.516C18,8.335,17.335,9,16.516,9H1.484C0.665,9,0,8.335,0,7.516l0,0c0-0.82,0.665-1.484,1.484-1.484 h15.031C17.335,6.031,18,6.696,18,7.516L18,7.516z"/>
          <path fill="#424242" d="M18,13.516C18,14.335,17.335,15,16.516,15H1.484C0.665,15,0,14.335,0,13.516l0,0 c0-0.82,0.665-1.484,1.484-1.484h15.031C17.335,12.031,18,12.696,18,13.516L18,13.516z"/>
        </svg>
      </a>

    </nav>

  </div>
</header>

 <div class="page-content">
    <div class="wrapper">
    <h2>
    {0}'s Communications
    </h2>
    <hr>
    {1} 
    </div>
</div>

<footer class="site-footer">

  <div class="wrapper">
    <div class="row">
          <div class="col-sm-12">Westi YA Communications Platform</div>
          <div class="col-sm-12">(c)2016</div>
    </div>
  </div>

</footer>

</body>

"""
