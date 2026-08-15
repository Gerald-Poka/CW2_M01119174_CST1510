"""Inline JavaScript for the dashboard view.

Returns the ECharts initialisation script embedded in ``{% block extra_js %}``.
The chart data is read from the ``PAGE_DATA`` global defined by the template.
"""


def build_js(context):
    return """
function renderBar(el, categories, values) {
    var chart = echarts.init(document.getElementById(el));
    chart.setOption({
        tooltip: {},
        grid: { left: 40, right: 20, top: 20, bottom: 40 },
        xAxis: { type: 'category', data: categories },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: values, itemStyle: { color: '#26a69a' }, barMaxWidth: 42 }]
    });
    window.addEventListener('resize', function () { chart.resize(); });
}
renderBar('incident-category-chart', PAGE_DATA.incident_category.keys, PAGE_DATA.incident_category.values);
renderBar('incident-status-chart', PAGE_DATA.incident_status.keys, PAGE_DATA.incident_status.values);
renderBar('ticket-status-chart', PAGE_DATA.ticket_status.keys, PAGE_DATA.ticket_status.values);
renderBar('ticket-assignee-chart', PAGE_DATA.ticket_assignee.keys, PAGE_DATA.ticket_assignee.values);
renderBar('metadata-chart', PAGE_DATA.metadata.keys, PAGE_DATA.metadata.values);
"""
