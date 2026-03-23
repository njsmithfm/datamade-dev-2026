import React, { useEffect, useState } from "react";

import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";

import "leaflet/dist/leaflet.css";

import RAW_COMMUNITY_AREAS from "../../../data/raw/community-areas.geojson";

function YearSelect({ filterVal, setFilterVal }) {
  // Filter by the permit issue year for each restaurant
  const startYear = 2026;
  const years = [...Array(11).keys()].map((increment) => {
    return startYear - increment;
  });
  const options = years.map((year) => {
    return (
      <option value={year} key={year}>
        {year}
      </option>
    );
  });

  return (
    <>
      <label htmlFor="yearSelect" className="fs-3">
        Filter by year:{" "}
      </label>
      <select
        id="yearSelect"
        className="form-select form-select-lg mb-3"
        value={filterVal}
        onChange={(e) => setFilterVal(Number(e.target.value))}
      >
        {options}
      </select>
    </>
  );
}

export default function RestaurantPermitMap() {
  const communityAreaColors = ["#eff3ff", "#bdd7e7", "#6baed6", "#2171b5"];

  const [currentYearData, setCurrentYearData] = useState([]);
  const [year, setYear] = useState(2026);

  const yearlyDataEndpoint = `/map-data/?year=${year}`;

  useEffect(() => {
    fetch(yearlyDataEndpoint)
      .then((res) => res.json())
      .then((data) => {
        setCurrentYearData(data);
      })
      .catch(() => {
        setCurrentYearData([]);
      });
  }, [yearlyDataEndpoint]);

  const totalPermits = currentYearData.reduce(
    (sum, area) => sum + area.num_permits,
    0,
  );

  const maxNumPermits = currentYearData.reduce(
    (maxPermits, area) => Math.max(maxPermits, area.num_permits),
    0,
  );

  const permitsByAreaId = currentYearData.reduce((lookup, area) => {
    lookup[String(area.area_id)] = area.num_permits;
    return lookup;
  }, {});

  function getColor(percentageOfPermits) {
    if (percentageOfPermits === 0) {
      return communityAreaColors[0];
    }
    if (percentageOfPermits <= 0.05) {
      return communityAreaColors[1];
    }
    if (percentageOfPermits <= 0.12) {
      return communityAreaColors[2];
    }

    return communityAreaColors[3];
  }

  function setAreaInteraction(feature, layer) {
    const areaName = feature.properties.community;
    const areaId = feature.properties.area_numbe;
    const permitCount = permitsByAreaId[String(areaId)] || 0;
    const permitShare = totalPermits > 0 ? permitCount / totalPermits : 0;

    layer.setStyle({
      fillColor: getColor(permitShare),
      fillOpacity: 0.7,
      weight: 1,
      opacity: 1,
    });

    layer.on("mouseover", () => {
      layer.bindPopup(
        `<strong>${areaName}</strong><br/>Permits in ${year}: ${permitCount}<br/>Citywide share: ${(permitShare * 100).toFixed(1)}%`,
      );
      layer.openPopup();
    });

    layer.on("mouseout", () => {
      layer.closePopup();
    });
  }

  return (
    <>
      <YearSelect filterVal={year} setFilterVal={setYear} />
      <p className="fs-4">
        Restaurant permits issued this year: {totalPermits}
      </p>
      <p className="fs-4">
        Maximum number of restaurant permits in a single area: {maxNumPermits}
      </p>
      <MapContainer id="restaurant-map" center={[41.88, -87.62]} zoom={10}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png"
        />
        {currentYearData.length > 0 ? (
          <GeoJSON
            data={RAW_COMMUNITY_AREAS}
            onEachFeature={setAreaInteraction}
            key={`${year}-${maxNumPermits}-${totalPermits}`}
          />
        ) : null}
      </MapContainer>
    </>
  );
}
