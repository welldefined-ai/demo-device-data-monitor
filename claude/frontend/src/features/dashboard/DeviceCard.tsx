/**
 * Device card component with gauge and trend chart
 */

import React, { useEffect, useState } from 'react';
import { Card, Typography, Tag, Space } from 'antd';
import ReactECharts from 'echarts-for-react';
import { Device, getErrorMessage } from '../../lib/api';

const { Text, Title } = Typography;

interface DeviceReading {
  device_id: number;
  device_name: string;
  unit: string;
  value: number;
  timestamp: string;
  status: string;
  thresholds: { warning?: number; critical?: number } | null;
}

interface DeviceCardProps {
  device: Device;
  reading?: DeviceReading;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({ device, reading }) => {
  const [historicalData, setHistoricalData] = useState<Array<{ timestamp: string; value: number }>>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const readings = await fetch(`/api/devices/${device.id}/readings/current?limit=20`)
          .then(res => res.json());

        if (readings.readings) {
          const data = readings.readings.reverse().map((r: { timestamp: string; value: number }) => ({
            timestamp: new Date(r.timestamp).toLocaleTimeString(),
            value: r.value,
          }));
          setHistoricalData(data);
        }
      } catch (error) {
        console.error(getErrorMessage(error));
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000); // Refresh every 2s (aligned with readings)
    return () => clearInterval(interval);
  }, [device.id]);

  const getConnectionStatusColor = () => {
    const status = reading?.status || device.status;
    return status === 'online' ? 'success' : 'default';
  };

  const getValueColor = () => {
    const value = reading?.value ?? 0;
    const thresholds = device.thresholds;

    if (!thresholds) return '#000';

    if (thresholds.critical && value >= thresholds.critical) return '#ff4d4f'; // Red
    if (thresholds.warning && value >= thresholds.warning) return '#faad14'; // Yellow
    return '#52c41a'; // Green
  };

  const getGaugeOption = () => {
    const value = reading?.value ?? 0;
    const thresholds = device.thresholds;
    const max = thresholds?.critical ? thresholds.critical * 1.2 : 100;

    return {
      series: [
        {
          type: 'gauge',
          startAngle: 180,
          endAngle: 0,
          min: 0,
          max,
          splitNumber: 5,
          axisLine: {
            lineStyle: {
              width: 6,
              color: [
                [thresholds?.warning ? thresholds.warning / max : 0.7, '#52c41a'],
                [thresholds?.critical ? thresholds.critical / max : 0.9, '#faad14'],
                [1, '#ff4d4f'],
              ],
            },
          },
          pointer: {
            itemStyle: {
              color: 'auto',
            },
          },
          axisTick: {
            distance: -6,
            length: 4,
            lineStyle: {
              color: '#fff',
              width: 1,
            },
          },
          splitLine: {
            distance: -8,
            length: 8,
            lineStyle: {
              color: '#fff',
              width: 2,
            },
          },
          axisLabel: {
            distance: 12,
            fontSize: 10,
          },
          detail: {
            valueAnimation: true,
            formatter: `{value} ${device.unit}`,
            fontSize: 16,
            offsetCenter: [0, '70%'],
          },
          data: [{ value }],
        },
      ],
    };
  };

  const getTrendOption = () => {
    const thresholds = device.thresholds;
    const maxValue = Math.max(...historicalData.map(d => d.value), thresholds?.critical || 100);

    // Create threshold markLines and background visualMap
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const markLine: any = {
      data: [],
      symbol: 'none',
      label: { show: true, position: 'end', fontSize: 10 },
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
      grid: {
        left: 45,
        right: 15,
        top: 20,
        bottom: 40,
      },
      xAxis: {
        type: 'category',
        data: historicalData.map(d => d.timestamp),
        axisLabel: {
          fontSize: 10,
          rotate: 30,
          interval: Math.floor(historicalData.length / 4), // Show every 4th label
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: { fontSize: 10 },
        min: 0,
        max: maxValue * 1.1,
      },
      visualMap: thresholds
        ? {
            show: false,
            pieces: [
              { lte: thresholds.warning || 0, color: 'rgba(82, 196, 26, 0.1)' }, // Green
              {
                gt: thresholds.warning || 0,
                lte: thresholds.critical || 0,
                color: 'rgba(250, 173, 20, 0.1)',
              }, // Yellow
              { gt: thresholds.critical || 0, color: 'rgba(255, 77, 79, 0.1)' }, // Red
            ],
            dimension: 1,
          }
        : undefined,
      series: [
        {
          data: historicalData.map(d => d.value),
          type: 'line',
          smooth: true,
          lineStyle: { width: 2 },
          itemStyle: { color: '#1890ff' },
          areaStyle: {},
          markLine: markLine.data.length > 0 ? markLine : undefined,
        },
      ],
      tooltip: {
        trigger: 'axis',
        formatter: (params: { name: string; value: number }[]) => {
          const point = params[0];
          return `${point.name}<br/>Value: ${point.value} ${device.unit}`;
        },
      },
    };
  };

  return (
    <Card size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text strong>{device.name}</Text>
          <Tag color={getConnectionStatusColor()}>
            {reading?.status?.toUpperCase() || device.status.toUpperCase()}
          </Tag>
        </div>

        <div style={{ textAlign: 'center', margin: '8px 0' }}>
          <Title level={2} style={{ margin: 0, color: getValueColor() }}>
            {reading?.value ? reading.value.toFixed(1) : '-'}
          </Title>
          <Text type="secondary">{device.unit}</Text>
        </div>

        <Text type="secondary" style={{ fontSize: 12, textAlign: 'center', display: 'block' }}>
          {reading?.timestamp
            ? `Updated: ${new Date(reading.timestamp).toLocaleTimeString()}`
            : 'No data'}
        </Text>

        <ReactECharts option={getGaugeOption()} style={{ height: '180px' }} />

        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>Recent Trend</Text>
          <ReactECharts option={getTrendOption()} style={{ height: '150px' }} />
        </div>
      </Space>
    </Card>
  );
};
