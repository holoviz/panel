import pytest
from script import to_product_bids_list, to_where_list

@pytest.mark.parametrize(["product_bids", "expected"], (
    ("1580571", "'1580571'"),
    ("1580571,1571961", "'1580571','1571961'"),
    ("1580571, 1571961", "'1580571','1571961'"),
))
def test_to_list(product_bids, expected):
    assert to_product_bids_list(product_bids)==expected

def test_to_where_line():
    row = {'product_bid': '1580571', 'price_provider_shortname': 'LIM', 'price_source_shortname': 'EPEX', 'value_type_shortname': 'Cls', 'delivery_period_type_shortname': 'HR', 'tickercode': 'EPEX.AUSTRIA.AUCTION.DA.HOUR'}
    assert to_where_list(row)=="product_bid='1580571' AND price_provider_shortname='LIM' AND price_source_shortname='EPEX' AND value_type_shortname='Cls' AND delivery_period_type_shortname='HR' AND tickercode='EPEX.AUSTRIA.AUCTION.DA.HOUR'"
