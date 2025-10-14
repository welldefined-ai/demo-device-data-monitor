import React, { useEffect, useMemo, useState } from 'react';
import { Button, Card, Form, Input, InputNumber, Modal, Space, Table, Tag, message } from 'antd';
import { api } from '../../lib/api';
import type { Device, DeviceStatus } from '../../types';

type DeviceForm = {
  name: string;
  description?: string;
  unit?: string;
  sampling_interval?: number;
  thresholds?: string | Record<string, unknown>;
  modbus_config?: string | Record<string, unknown>;
};

export function DevicesPage(): JSX.Element {
  const [data, setData] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm<DeviceForm>();
  const [msgApi, ctx] = message.useMessage();

  const load = async () => {
    setLoading(true);
    try {
      const devices = await api.get<Device[]>('/devices/');
      setData(devices);
    } catch (e: any) {
      msgApi.error(e?.message || 'Failed to load devices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const onCreate = async () => {
    try {
      const values = await form.validateFields();
      // Parse JSON fields if provided as string
      let thresholds: Record<string, unknown> = {};
      let modbus: Record<string, unknown> = {};
      if (typeof values.thresholds === 'string' && values.thresholds.trim()) {
        try {
          thresholds = JSON.parse(values.thresholds);
        } catch (_err: any) {
          msgApi.error('Invalid thresholds JSON');
          return;
        }
      } else if (values.thresholds && typeof values.thresholds === 'object') {
        thresholds = values.thresholds as Record<string, unknown>;
      }
      if (typeof values.modbus_config === 'string' && values.modbus_config.trim()) {
        try {
          modbus = JSON.parse(values.modbus_config);
        } catch (_err: any) {
          msgApi.error('Invalid Modbus config JSON');
          return;
        }
      } else if (values.modbus_config && typeof values.modbus_config === 'object') {
        modbus = values.modbus_config as Record<string, unknown>;
      }
      await api.post<Device>('/devices/', {
        name: values.name,
        description: values.description || '',
        unit: values.unit || '',
        sampling_interval: values.sampling_interval || 60,
        thresholds,
        modbus_config: modbus,
      });
      setOpen(false);
      form.resetFields();
      await load();
      msgApi.success('Device created');
    } catch (e: any) {
      if (e?.message) msgApi.error(e.message);
    }
  };

  const onDelete = async (id: number) => {
    try {
      await api.delete(`/devices/${id}`);
      await load();
      msgApi.success('Deleted');
    } catch (e: any) {
      msgApi.error(e?.message || 'Delete failed');
    }
  };

  const onTest = async (id: number) => {
    try {
      const res = await api.post<{ ok: boolean; error?: string }>(`/devices/${id}/test-connection`);
      if (res.ok) msgApi.success('Connection OK');
      else msgApi.warning(res?.error || 'Connection failed');
    } catch (e: any) {
      msgApi.error(e?.message || 'Test failed');
    }
  };

  const onLatest = async (id: number) => {
    try {
      const lst = await api.get<Array<{ timestamp: string; value: number }>>(`/devices/${id}/readings/current?limit=1`);
      if (!lst || lst.length === 0) {
        msgApi.info('No readings yet');
      } else {
        const r = lst[0];
        const when = new Date(r.timestamp).toLocaleString();
        msgApi.success(`Latest: ${r.value} @ ${when}`);
      }
    } catch (e: any) {
      msgApi.error(e?.message || 'Failed to fetch latest reading');
    }
  };

  const statusTag = (s: DeviceStatus) => (
    <Tag color={s === 'online' ? 'green' : s === 'error' ? 'red' : 'default'}>{s}</Tag>
  );

  const columns = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 80 },
      { title: 'Name', dataIndex: 'name' },
      { title: 'Unit', dataIndex: 'unit', width: 100 },
      { title: 'Interval (s)', dataIndex: 'sampling_interval', width: 120 },
      { title: 'Status', dataIndex: 'status', width: 120, render: (v: DeviceStatus) => statusTag(v) },
      {
        title: 'Actions',
        width: 300,
        render: (_: any, r: Device) => (
          <Space>
            <Button size="small" onClick={() => onTest(r.id)}>Test</Button>
            <Button size="small" onClick={() => onLatest(r.id)}>Latest</Button>
            <Button danger size="small" onClick={() => onDelete(r.id)}>
              Delete
            </Button>
          </Space>
        ),
      },
    ],
    [],
  );

  return (
    <Card title="Devices" extra={<Button onClick={() => setOpen(true)}>New Device</Button>}>
      {ctx}
      <Table<Device> rowKey="id" loading={loading} columns={columns as any} dataSource={data} pagination={false} />
      <Modal title="Create Device" open={open} onCancel={() => setOpen(false)} onOk={onCreate} okText="Create">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input />
          </Form.Item>
          <Form.Item name="unit" label="Unit">
            <Input />
          </Form.Item>
          <Form.Item name="sampling_interval" label="Sampling Interval (s)">
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="thresholds" label="Thresholds (JSON)">
            <Input.TextArea placeholder='{"warning": 70, "critical": 90}' autoSize />
          </Form.Item>
          <Form.Item name="modbus_config" label="Modbus Config (JSON)">
            <Input.TextArea placeholder='{"type":"tcp","host":"simulator","port":1502,"unit_id":1,"register":0,"data_type":"uint16"}' autoSize />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
