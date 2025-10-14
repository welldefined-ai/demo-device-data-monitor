import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Card, Col, Row, Tag, Typography, message } from 'antd';
import * as echarts from 'echarts';
import { api } from '../../lib/api';
import type { Device } from '../../types';

type Reading = { timestamp: string; value: number };

function useDeviceFeed(deviceId: number) {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [status, setStatus] = useState<'online' | 'offline' | 'error'>('offline');
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number>(0);

  useEffect(() => {
    let mounted = true;
    // Load initial recent readings
    (async () => {
      try {
        const lst = await api.get<Reading[]>(`/devices/${deviceId}/readings/current?limit=20`);
        if (!mounted) return;
        setReadings(lst.slice().reverse()); // ascending order for charts
      } catch {
        // ignore
      }
    })();

    const connect = () => {
      const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/live?device_id=${deviceId}`);
      wsRef.current = ws;
      ws.onopen = () => {
        retryRef.current = 0;
      };
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === 'reading') {
            setReadings((prev) => {
              const next = [...prev, { timestamp: msg.timestamp, value: msg.value }];
              return next.slice(-20);
            });
            setStatus(msg.status as any);
          }
        } catch {
          // ignore
        }
      };
      ws.onclose = () => {
        if (!mounted) return;
        // exponential backoff up to ~5s
        retryRef.current = Math.min(retryRef.current + 1, 5);
        setTimeout(connect, retryRef.current * 500);
      };
      ws.onerror = () => {
        ws.close();
      };
    };
    connect();
    return () => {
      mounted = false;
      wsRef.current?.close();
    };
  }, [deviceId]);

  return { readings, status };
}

function Gauge({ value, thresholds }: { value: number; thresholds: any }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    const warn = Number(thresholds?.warning ?? 0);
    const crit = Number((thresholds?.critical ?? warn) || 100);
    const max = Math.max(crit || 100, value * 1.2);
    chart.setOption({
      series: [
        {
          type: 'gauge',
          min: 0,
          max,
          axisLine: {
            lineStyle: {
              color: [
                [warn > 0 ? warn / max : 0.6, '#52c41a'],
                [crit > 0 ? crit / max : 0.85, '#faad14'],
                [1, '#ff4d4f'],
              ],
            },
          },
          detail: { valueAnimation: true, formatter: '{value}' },
          data: [{ value }],
        },
      ],
    });
    const handle = () => chart.resize();
    window.addEventListener('resize', handle);
    return () => {
      chart.dispose();
      window.removeEventListener('resize', handle);
    };
  }, [value, thresholds]);
  return <div ref={ref} style={{ width: '100%', height: 160 }} />;
}

function Sparkline({ readings, thresholds }: { readings: Reading[]; thresholds: any }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    const data = readings.map((r) => [r.timestamp, r.value]);
    const warn = Number(thresholds?.warning ?? NaN);
    const crit = Number(thresholds?.critical ?? NaN);
    chart.setOption({
      grid: { left: 30, right: 10, top: 10, bottom: 30 },
      xAxis: { type: 'time', axisLabel: { show: false }, axisTick: { show: false } },
      yAxis: { type: 'value', axisLabel: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
      series: [
        {
          type: 'line',
          showSymbol: false,
          smooth: true,
          data,
          lineStyle: { width: 2 },
          areaStyle: {},
        },
        ...(isFinite(warn)
          ? ([{ type: 'line', data: data.map((d) => [d[0], warn]), lineStyle: { color: '#faad14', type: 'dashed' }, symbol: 'none' }] as any)
          : []),
        ...(isFinite(crit)
          ? ([{ type: 'line', data: data.map((d) => [d[0], crit]), lineStyle: { color: '#ff4d4f', type: 'dashed' }, symbol: 'none' }] as any)
          : []),
      ],
    });
    const handle = () => chart.resize();
    window.addEventListener('resize', handle);
    return () => {
      chart.dispose();
      window.removeEventListener('resize', handle);
    };
  }, [JSON.stringify(readings), thresholds]);
  return <div ref={ref} style={{ width: '100%', height: 120 }} />;
}

function DeviceCard({ d }: { d: Device }) {
  const { readings, status } = useDeviceFeed(d.id);
  const latest = readings.length ? readings[readings.length - 1] : null;
  const color = useMemo(() => (status === 'online' ? 'green' : status === 'error' ? 'red' : 'default'), [status]);
  return (
    <Card title={
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>{d.name}</span>
        <Tag color={color}>{status}</Tag>
      </div>
    }>
      <Row gutter={16}>
        <Col span={12}>
          <Typography.Text type="secondary">Current</Typography.Text>
          <div style={{ fontSize: 24, fontWeight: 600 }}>{latest ? `${latest.value} ${d.unit || ''}` : '—'}</div>
          <div style={{ color: '#888' }}>{latest ? new Date(latest.timestamp).toLocaleString() : 'No data'}</div>
          <div style={{ marginTop: 8 }}>
            <Gauge value={latest?.value ?? 0} thresholds={d.thresholds} />
          </div>
        </Col>
        <Col span={12}>
          <Typography.Text type="secondary">Recent</Typography.Text>
          <Sparkline readings={readings} thresholds={d.thresholds} />
        </Col>
      </Row>
    </Card>
  );
}

export function DashboardPage(): JSX.Element {
  const [devices, setDevices] = useState<Device[]>([]);
  const [msg, ctx] = message.useMessage();

  useEffect(() => {
    (async () => {
      try {
        const lst = await api.get<Device[]>(`/devices/`);
        setDevices(lst);
      } catch (e: any) {
        msg.error(e?.message || 'Failed to load devices');
      }
    })();
  }, []);

  return (
    <div>
      {ctx}
      <Typography.Title level={3}>Live Dashboard</Typography.Title>
      <Row gutter={[16, 16]}>
        {devices.map((d) => (
          <Col key={d.id} xs={24} md={12} lg={8} xl={6}>
            <DeviceCard d={d} />
          </Col>
        ))}
      </Row>
    </div>
  );
}
