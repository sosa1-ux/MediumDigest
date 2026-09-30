import networkx as nx
import requests

url = "https://www.data.va.gov/api/v3/views/95an-zhhy/query.json?accessType=DOWNLOAD"

response = requests.get(url)
data = response.json()

g = nx.Graph()
state_to_counties = {}

for this_county in data:

    fips = str(this_county['fips_code']).zfill(5)
    county_name = this_county['county_name']
    state_name = this_county['state']

    # Keep the disability data
    total_disability = this_county.get('total_disability_compensation')
    scd_100 = this_county.get('scd_rating_100')

    g.add_node(
        fips,
        name=county_name,
        state=state_name,
        total_disability_compensation=total_disability,
        scd_rating_100=scd_100
    )

    if state_name not in state_to_counties:
        state_to_counties[state_name] = []

    state_to_counties[state_name].append((fips, county_name))


for state_name, counties in state_to_counties.items():

    for i, (left_fips, left_name) in enumerate(counties):

        left_data = g.nodes[left_fips]

        for right_fips, right_name in counties[i + 1:]:

            right_data = g.nodes[right_fips]

            left_total = left_data['total_disability_compensation']
            right_total = right_data['total_disability_compensation']

            left_scd = left_data['scd_rating_100']
            right_scd = right_data['scd_rating_100']

            # Skip counties with missing disability data
            if left_total is None or right_total is None:
                continue

            if left_scd is None or right_scd is None:
                continue

            # Are total disability amounts within 10%?
            total_similar = (
                abs(int(left_total) - int(right_total))
                / max(int(left_total), int(right_total))
                <= 0.10
            )

            # Are 100% SCD counts within 10%?
            scd_similar = (
                abs(int(left_scd) - int(right_scd))
                / max(int(left_scd), int(right_scd))
                <= 0.10
            )

            if total_similar and scd_similar:

                g.add_edge(left_fips, right_fips)

                print(
                    left_name,
                    "<->",
                    right_name,
                    f"({state_name})"
                )
            