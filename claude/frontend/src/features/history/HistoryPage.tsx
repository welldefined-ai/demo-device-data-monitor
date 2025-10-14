/**
 * Historical data page with time range selection and CSV export
 */

import React, { useEffect, useState } from 'react';
import { Card, Select, DatePicker, Button, Spin, message, Space, Typography } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs, { Dayjs } from 'dayjs';
import { Device, devicesApi, getErrorMessage } from '../../lib/api';

const { RangePicker } = DatePicker;
const { Title } = Typography;

interface Reading {
  timestamp: string;
  value: number;
}

export const HistoryPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDeviceIds, setSelectedDeviceIds] = useState<number[]>([]);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(1, 'day').startOf('day'),
    dayjs().endOf('day'),
  ]);
  const [deviceReadings, setDeviceReadings] = useState<Map<number, Reading[]>>(new Map());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDevices();
  }, []);

  useEffect(() => {
    if (selectedDeviceIds.length > 0) {
      loadHistoricalData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDeviceIds, dateRange]);

  const loadDevices = async () => {
    try {
      const response = await devicesApi.list();
      setDevices(response.devices);
      if (response.devices.length > 0) {
        setSelectedDeviceIds([response.devices[0].id]);
      }
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const loadHistoricalData = async () => {
    if (selectedDeviceIds.length === 0) return;

    setLoading(true);
    const newReadings = new Map<number, Reading[]>();

    try {
      const start = dateRange[0].toISOString();
      const end = dateRange[1].toISOString();

      // Fetch data for all selected devices in parallel
      await Promise.all(
        selectedDeviceIds.map(async (deviceId) => {
          try {
            const res = await fetch(
              `/api/devices/${deviceId}/readings/history?start=${start}&end=${end}`,
              { credentials: 'include' }
            );

            if (!res.ok) {
              if (res.status === 500) {
                throw new Error('Server error occurred. Please try again.');
              }
              const errorData = await res.json().catch(() => ({ detail: 'Unknown error' }));
              throw new Error(errorData.detail || `Error ${res.status}`);
            }

            const response = await res.json();
            if (response.readings) {
              newReadings.set(deviceId, response.readings);
            }
          } catch (error) {
            console.error(`Error loading device ${deviceId}:`, error);
          }
        })
      );

      setDeviceReadings(newReadings);
    } catch (error) {
      message.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (selectedDeviceIds.length === 0) return;

    const start = dateRange[0].toISOString();
    const end = dateRange[1].toISOString();

    // Export first selected device
    const url = `/api/devices/${selectedDeviceIds[0]}/readings/export?start=${start}&end=${end}`;
    window.open(url, '_blank');
    message.success('Export started');
  };

  const getChartOption = () => {
    if (selectedDeviceIds.length === 0 || deviceReadings.size === 0) return {};

    // Group devices by unit to determine Y-axes
    const unitGroups = new Map<string, number[]>();
    selectedDeviceIds.forEach(id => {
      const device = devices.find(d => d.id === id);
      if (device) {
        if (!unitGroups.has(device.unit)) {
          unitGroups.set(device.unit, []);
        }
        unitGroups.get(device.unit)!.push(id);
      }
    });

    // Create Y-axes (max 2 for readability)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const yAxes: any[] = Array.from(unitGroups.keys()).slice(0, 2).map((unit, index) => ({
      type: 'value',
      name: unit,
      position: index === 0 ? 'left' : 'right',
      axisLabel: { fontSize: 11 },
    }));

    // Create series for each device with colored segments based on thresholds
    const colors = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2'];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const series: any[] = [];

    selectedDeviceIds.forEach((deviceId, index) => {
      const device = devices.find(d => d.id === deviceId);
      const readings = deviceReadings.get(deviceId);

      if (!device || !readings) return;

      // Determine which Y-axis to use
      const yAxisIndex = Array.from(unitGroups.keys()).indexOf(device.unit);

      // Color curve segments based on thresholds
      const data = readings.map(r => {
        let color = colors[index % colors.length];
        if (device.thresholds) {
          if (device.thresholds.critical && r.value >= device.thresholds.critical) {
            color = '#ff4d4f'; // Red
          } else if (device.thresholds.warning && r.value >= device.thresholds.warning) {
            color = '#faad14'; // Yellow
          } else {
            color = '#52c41a'; // Green
          }
        }
        return { value: r.value, itemStyle: { color } };
      });

      series.push({
        name: device.name,
        type: 'line',
        yAxisIndex: Math.min(yAxisIndex, yAxes.length - 1),
        data,
        smooth: true,
        lineStyle: { width: 2 },
        emphasis: { focus: 'series' },
      });
    });

    // Get all unique timestamps
    const allTimestamps = new Set<string>();
    deviceReadings.forEach(readings => {
      readings.forEach(r => allTimestamps.add(dayjs(r.timestamp).format('MM-DD HH:mm')));
    });
    const timestamps = Array.from(allTimestamps).sort();

    return {
      title: {
        text: 'Historical Trends',
        left: 'center',
      },
      legend: {
        data: selectedDeviceIds.map(id => devices.find(d => d.id === id)?.name || ''),
        top: 30,
      },
      grid: {
        left: 60,
        right: yAxes.length > 1 ? 60 : 40,
        top: 80,
        bottom: 80,
      },
      xAxis: {
        type: 'category',
        data: timestamps,
        axisLabel: {
          rotate: 45,
          interval: Math.max(1, Math.floor(timestamps.length / 15)),
          fontSize: 10,
        },
      },
      yAxis: yAxes,
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100,
        },
        {
          start: 0,
          end: 100,
        },
      ],
      series,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
    };
  };

  return (
    <Card>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={3}>Historical Data</Title>
        </div>

        <Space wrap>
          <Select
            mode="multiple"
            style={{ minWidth: 300 }}
            placeholder="Select devices"
            value={selectedDeviceIds}
            onChange={setSelectedDeviceIds}
            maxTagCount="responsive"
            options={devices.map(d => ({
              value: d.id,
              label: `${d.name} (${d.unit})`,
            }))}
          />

          <RangePicker
            value={dateRange}
            onChange={(dates) => {
              if (dates && dates[0] && dates[1]) {
                setDateRange([
                  dates[0].startOf('day'),
                  dates[1].endOf('day'),
                ]);
              }
            }}
            format="YYYY-MM-DD"
          />

          <Button
            icon={<DownloadOutlined />}
            onClick={handleExport}
            disabled={selectedDeviceIds.length === 0 || deviceReadings.size === 0}
          >
            Export CSV
          </Button>
        </Space>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" tip="Loading historical data..." />
          </div>
        ) : deviceReadings.size === 0 ? (
          <div style={{ textAlign: 'center', padding: 50, color: '#999' }}>
            No data available for selected time range
          </div>
        ) : (
          <ReactECharts
            option={getChartOption()}
            style={{ height: '500px' }}
            opts={{ renderer: 'canvas' }}
          />
        )}

        {!loading && deviceReadings.size > 0 && (
          <div style={{ textAlign: 'center', color: '#999', fontSize: 12 }}>
            {selectedDeviceIds.length} device(s) selected •{' '}
            {Array.from(deviceReadings.values()).reduce((sum, r) => sum + r.length, 0)} total readings •{' '}
            {dateRange[0].format('YYYY-MM-DD')} to {dateRange[1].format('YYYY-MM-DD')}
          </div>
        )}
      </Space>
    </Card>
  );
};
