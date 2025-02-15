# Template section

head_js_template = """<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        /* Tab styling */
        .tab-container {
            display: flex;
            justify-content: center;
            border-bottom: 2px solid #ddd;
            margin-bottom: 10px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            font-size: 16px;
            font-family: Arial, sans-serif;
            border: none;
            background: none;
            outline: none;
            color: #555;
        }
        .tab:hover {
            color: #000;
        }
        .tab.active {
            font-weight: bold;
            color: #000;
            border-bottom: 3px solid #007bff;
        }
        .tab-content {
            display: none;
            padding: 10px;
            width: 100%;
        }
        .tab-content.active {
            display: block;
            width: 100%;
        }
    </style>
    <script>
        function switchTab(tabName) {
            // Hide all tab content
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });

            // Deactivate all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show the selected tab and mark it active
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[data-tab='${tabName}']`).classList.add('active');
        }
    </script>
</head>
<body>

<!-- Tab Navigation -->
<div class="tab-container">
    <button class="tab active" data-tab="All Years" onclick="switchTab('All Years')">All Years</button>
    <button class="tab" data-tab="Last Year" onclick="switchTab('Last Year')">Last Year</button>
</div>
"""

tab_1_template = """
<!-- Tab 1 Content -->
<div id="All Years" class="tab-content active">
    {content}
</div>
"""

tab_2_template = """
<!-- Tab 2 Content -->
<div id="Last Year" class="tab-content">
    {content}
</div>
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
