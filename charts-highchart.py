from nicegui import ui
import requests

# timeline version https://www.highcharts.com/demo/stock/inverted-navigator
# more flags https://www.highcharts.com/demo/stock/flags-placement
# https://www.highcharts.com/demo/stock/flags-shapes
# https://www.highcharts.com/demo/stock/flags-general

# data is at https://cdn.jsdelivr.net/gh/highcharts/highcharts@v10.3.3/samples/data/usdeur.json

data = requests.get('https://cdn.jsdelivr.net/gh/highcharts/highcharts/samples/data/usdeur.json').json()

ui.highchart({

        'navigator': {
              'enabled': True
        },
        'rangeSelector': { 'enabled': True,
    'selected': 0,
    'buttons': [{
        'type': 'month',
        'count': 1,
        'text': '1m'
    }, {
        'type': 'month',
        'count': 3,
        'text': '3m'
    }, {
        'type': 'month',
        'count': 6,
        'text': '6m'
    }, {
        'type': 'ytd',
        'text': 'YTD'
    }, {
        'type': 'year',
        'count': 1,
        'text': '1y'
    }, {
        'type': 'all',
        'text': 'All'
    }]
},

        'title': {
            'text': 'USD to EUR exchange rate'
        },

        'tooltip': {
            'style': {
                'width': '200px'
            },
            'valueDecimals': 4,
            'shared': True
        },

        'yAxis': {
            'title': {
                'text': 'Exchange rate'
            }
        },

        'series': [{
            'name': 'USD to EUR',
            'data': data,
            'id': 'dataseries'

        # the event marker flags
        }, { 'name': 'Events',
            'type': 'flags',
            'accessibility': {
                'exposeAsGroupOnly': True,
                'description': 'Flagged events.'
            },
            'data': [{
                'x': 1638409600000,
                'title': 'A',
                'text': 'Some event with a description'
            }, {
                'x': 1639536000000,
                'title': 'B',
                'text': 'Some event with a description'
            }, {
                'x': 1640217600000,
                'title': 'C',
                'text': 'Some event with a description'
            }],
            'onSeries': 'dataseries',
            'shape': 'circlepin',
            'width': 16
        }],
        'xAxis': {
                 'type': 'datetime'
        }
    }, extras=['stock', 'exporting', 'accessibility']).classes('w-full h-564')



ui.run(show=False)

