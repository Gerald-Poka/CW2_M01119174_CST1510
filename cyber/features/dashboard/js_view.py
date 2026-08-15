"""Inline JavaScript for the dashboard view.

Returns the ECharts initialisation script embedded in ``{% block extra_js %}``.
The chart data is read from the ``PAGE_DATA`` global defined by the template.
"""


def build_js(context):
    return """
document.addEventListener('DOMContentLoaded', function () {
    function renderBar(el, categories, values) {
        var dom = document.getElementById(el);
        if (!dom) return;
        var chart = echarts.getInstanceByDom(dom) || echarts.init(dom);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            grid: { left: 40, right: 20, top: 20, bottom: 40 },
            xAxis: { type: 'category', data: categories || [] },
            yAxis: { type: 'value' },
            series: [{ type: 'bar', data: values || [], itemStyle: { color: '#1e3a5f', borderRadius: [4, 4, 0, 0] }, barMaxWidth: 42 }]
        });
        window.addEventListener('resize', function () { chart.resize(); });
    }

    function initAllCharts() {
        if (typeof PAGE_DATA === 'undefined') return;
        if (PAGE_DATA.incident_category) renderBar('incident-category-chart', PAGE_DATA.incident_category.keys, PAGE_DATA.incident_category.values);
        if (PAGE_DATA.incident_status) renderBar('incident-status-chart', PAGE_DATA.incident_status.keys, PAGE_DATA.incident_status.values);
        if (PAGE_DATA.ticket_status) renderBar('ticket-status-chart', PAGE_DATA.ticket_status.keys, PAGE_DATA.ticket_status.values);
        if (PAGE_DATA.ticket_assignee) renderBar('ticket-assignee-chart', PAGE_DATA.ticket_assignee.keys, PAGE_DATA.ticket_assignee.values);
        if (PAGE_DATA.metadata) renderBar('metadata-chart', PAGE_DATA.metadata.keys, PAGE_DATA.metadata.values);
    }

    initAllCharts();
    var tabLinks = document.querySelectorAll('a[data-bs-toggle="tab"]');
    tabLinks.forEach(function (tab) {
        tab.addEventListener('shown.bs.tab', function () {
            initAllCharts();
        });
    });
});
"""
