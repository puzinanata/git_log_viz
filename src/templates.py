# #1. Template section

head_js_template = """<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
"""
head_template = """<html>
<head>

</head>
<body>
"""

tail_template = """
</body>

</html>"""
graph_js_template = """
    <div id='{div_name}'></div>
    <script>
        var plotly_data = {content}
        Plotly.react('{div_name}', plotly_data.data, plotly_data.layout);
    </script>
"""

graph_js_double_template = """
    <div style="display: flex; justify-content: space-between; gap: 20px;">
        <div id='{div_name1}' style="flex: 1;"></div>
        <div id='{div_name2}' style="flex: 1;"></div>
    </div>
    <script>
        // First graph
        var plotly_data_1 = {content1};
        Plotly.react('{div_name1}', plotly_data_1.data, plotly_data_1.layout);

        // Second graph
        var plotly_data_2 = {content2};
        Plotly.react('{div_name2}', plotly_data_2.data, plotly_data_2.layout);
    </script>
"""

table_js_template = """
    <p style="text-align: center; font-size: 18px; font-family: Arial, sans-serif; margin: 30px 0; color:#444">
        Top Authors
    </p>
{}
""".format(graph_js_template)

image_template = """
<img src="{path}" style="max-width: 100%; height: auto;">
"""

image_double_template = """
<div style="display: flex; justify-content: space-between; gap: 20px;">
    <img src="{path1}" style="max-width: 48%; height: auto;">
    <img src="{path2}" style="max-width: 48%; height: auto;">
</div>
"""

table_image_template = """
    <p style="text-align: center; font-size: 18px; font-family: Arial, sans-serif; margin: 30px 0; color:#444">
        Top Authors
    </p>
{}
""".format(image_template)
