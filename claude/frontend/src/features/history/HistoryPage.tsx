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
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(1, 'hour'),
    dayjs(),
  ]);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDevices();
  }, []);

  useEffect(() => {
    if (selectedDeviceId) {
      const device = devices.find(d => d.id === selectedDeviceId);
      setSelectedDevice(device || null);
      loadHistoricalData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDeviceId, dateRange]);

  const loadDevices = async () => {
    try {
      const response = await devicesApi.list();
      setDevices(response.devices);
      if (response.devices.length > 0) {
        setSelectedDeviceId(response.devices[0].id);
      }
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const loadHistoricalData = async () => {
    if (!selectedDeviceId) return;

    setLoading(true);
    try {
      const start = dateRange[0].toISOString();
      const end = dateRange[1].toISOString();

      const res = await fetch(
        `/api/devices/${selectedDeviceId}/readings/history?start=${start}&end=${end}`,
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
        setReadings(response.readings);
      } else {
        setReadings([]);
      }
    } catch (error) {
      message.error(getErrorMessage(error));
      setReadings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!selectedDeviceId) return;

    const start = dateRange[0].toISOString();
    const end = dateRange[1].toISOString();

    const url = `/api/devices/${selectedDeviceId}/readings/export?start=${start}&end=${end}`;
    window.open(url, '_blank');
    message.success('Export started');
  };

  const getChartOption = () => {
    if (!selectedDevice) return {};

    const thresholds = selectedDevice.thresholds;
    const data = readings.map(r => ({
      time: dayjs(r.timestamp).format('MM-DD HH:mm:ss'),
      value: r.value,
    }));

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const markLine: any = {
      data: [],
      symbol: 'none',
      label: { show: true, position: 'insideEndTop', fontSize: 12 },
    };

    if (thresholds?.warning) {
      markLine.data.push({
        yAxis: thresholds.warning,
        lineStyle: { color: '#faad14', width: 2, type: 'dashed' },
        label: { formatter: 'Warning' },
      });
    }

    if (thresholds?.critical) {
      markLine.data.push({
        yAxis: thresholds.critical,
        lineStyle: { color: '#ff4d4f', width: 2, type: 'dashed' },
        label: { formatter: 'Critical' },
      });
    }

    return {
      title: {
        text: `${selectedDevice.name} - Historical Trends`,
        left: 'center',
      },
      grid: {
        left: 60,
        right: 40,
        top: 60,
        bottom: 60,
      },
      xAxis: {
        type: 'category',
        data: data.map(d => d.time),
        axisLabel: {
          rotate: 45,
          interval: Math.max(1, Math.floor(data.length / 10)),
        },
      },
      yAxis: {
        type: 'value',
        name: selectedDevice.unit,
      },
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
      visualMap: thresholds
        ? {
            show: false,
            pieces: [
              { lte: thresholds.warning || 0, color: 'rgba(82, 196, 26, 0.2)' },
              {
                gt: thresholds.warning || 0,
                lte: thresholds.critical || 0,
                color: 'rgba(250, 173, 20, 0.2)',
              },
              { gt: thresholds.critical || 0, color: 'rgba(255, 77, 79, 0.2)' },
            ],
            dimension: 1,
          }
        : undefined,
      series: [
        {
          data: data.map(d => d.value),
          type: 'line',
          smooth: true,
          lineStyle: { width: 2 },
          areaStyle: {},
          markLine: markLine.data.length > 0 ? markLine : undefined,
        },
      ],
      tooltip: {
        trigger: 'axis',
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        formatter: (params: any) => {
          const point = params[0];
          return `${point.axisValue}<br/>Value: ${point.value} ${selectedDevice.unit}`;
        },
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
            style={{ width: 250 }}
            placeholder="Select device"
            value={selectedDeviceId}
            onChange={setSelectedDeviceId}
            options={devices.map(d => ({
              value: d.id,
              label: `${d.name} (${d.unit})`,
            }))}
          />

          <RangePicker
            showTime
            value={dateRange}
            onChange={(dates) => {
              if (dates && dates[0] && dates[1]) {
                setDateRange([dates[0], dates[1]]);
              }
            }}
          />

          <Button
            icon={<DownloadOutlined />}
            onClick={handleExport}
            disabled={!selectedDeviceId || readings.length === 0}
          >
            Export CSV
          </Button>
        </Space>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" tip="Loading historical data..." />
          </div>
        ) : readings.length === 0 ? (
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

        {!loading && readings.length > 0 && (
          <div style={{ textAlign: 'center', color: '#999', fontSize: 12 }}>
            {readings.length} readings from {dayjs(readings[0].timestamp).format('YYYY-MM-DD HH:mm:ss')} to{' '}
            {dayjs(readings[readings.length - 1].timestamp).format('YYYY-MM-DD HH:mm:ss')}
          </div>
        )}
      </Space>
    </Card>
  );
};
