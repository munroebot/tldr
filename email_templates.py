BODY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<title>LVDS Daily Summary</title>

<style type="text/css">
    h4 {{ padding-bottom: 0px; margin-bottom: 0px; border-bottom: 3px solid #A9A9A9; }}
    pre {{ padding-top: 5px; margin-top: 0px; }}
</style>

</head>
<body>
<h3>LVDS Daily Summary</h3>

<h4>AR Points:</h4>
<pre>{}</pre>

<h4>Homework (Summary):</h4>
<pre>{}</pre>

<h4>Homework (Long Description):</h4>
<pre>{}</pre>

</body>
</html>
"""

    BODY_TEXT = """
LVDS Daily Summary
------------------
    
AR Points: {}

Homework Summary:
=================
{}

Homework Long Description:
==========================
{}
"""