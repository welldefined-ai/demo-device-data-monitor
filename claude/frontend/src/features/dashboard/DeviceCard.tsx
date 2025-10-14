/**
 * Device card component with gauge and trend chart
 */

import React, { useEffect, useState } from 'react';
import { Card, Typography, Tag, Statistic, Space } from 'antd';
import ReactECharts from 'echarts-for-react';
import { Device, getErrorMessage } from '../../lib/api';

const { Text } = Typography;

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
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [device.id]);

  const getStatusColor = () => {
    const value = reading?.value ?? 0;
    const thresholds = device.thresholds;

    if (!thresholds) return 'default';

    if (thresholds.critical && value >= thresholds.critical) return 'error';
    if (thresholds.warning && value >= thresholds.warning) return 'warning';
    return 'success';
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
    return {
      grid: {
        left: 40,
        right: 10,
        top: 10,
        bottom: 30,
      },
      xAxis: {
        type: 'category',
        data: historicalData.map(d => d.timestamp),
        axisLabel: { fontSize: 10, rotate: 45 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { fontSize: 10 },
      },
      series: [
        {
          data: historicalData.map(d => d.value),
          type: 'line',
          smooth: true,
          lineStyle: { width: 2 },
          itemStyle: { color: '#1890ff' },
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
          <Tag color={getStatusColor()}>
            {reading?.status?.toUpperCase() || device.status.toUpperCase()}
          </Tag>
        </div>

        <Statistic
          title="Current Value"
          value={reading?.value ?? '-'}
          suffix={device.unit}
          valueStyle={{ fontSize: 24 }}
        />

        <Text type="secondary" style={{ fontSize: 12 }}>
          {reading?.timestamp
            ? `Updated: ${new Date(reading.timestamp).toLocaleTimeString()}`
            : 'No data'}
        </Text>

        <ReactECharts option={getGaugeOption()} style={{ height: '180px' }} />

        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>Recent Trend</Text>
          <ReactECharts option={getTrendOption()} style={{ height: '120px' }} />
        </div>
      </Space>
    </Card>
  );
};
