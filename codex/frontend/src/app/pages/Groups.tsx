import React, { useEffect, useMemo, useState } from 'react';
import { Button, Card, Form, Input, Modal, Space, Table, message, Select } from 'antd';
import { api } from '../../lib/api';
import type { Group, Device } from '../../types';

export function GroupsPage(): JSX.Element {
  const [groups, setGroups] = useState<Group[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [assignOpen, setAssignOpen] = useState(false);
  const [currentGroup, setCurrentGroup] = useState<Group | null>(null);
  const [form] = Form.useForm<{ name: string; description?: string }>();
  const [assignForm] = Form.useForm<{ device_id: number }>();
  const [msg, ctx] = message.useMessage();

  const load = async () => {
    setLoading(true);
    try {
      const [gs, ds] = await Promise.all([api.get<Group[]>('/groups/'), api.get<Device[]>('/devices/')]);
      setGroups(gs);
      setDevices(ds);
    } catch (e: any) {
      msg.error(e?.message || 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const onCreate = async () => {
    const values = await form.validateFields();
    try {
      await api.post<Group>('/groups/', values);
      setOpen(false);
      form.resetFields();
      await load();
      msg.success('Group created');
    } catch (e: any) {
      msg.error(e?.message || 'Create failed');
    }
  };

  const onDelete = async (id: number) => {
    try {
      await api.delete(`/groups/${id}`);
      await load();
      msg.success('Deleted');
    } catch (e: any) {
      msg.error(e?.message || 'Delete failed');
    }
  };

  const onAssign = async () => {
    const values = await assignForm.validateFields();
    if (!currentGroup) return;
    try {
      await api.post(`/groups/${currentGroup.id}/devices/${values.device_id}`);
      setAssignOpen(false);
      assignForm.resetFields();
      msg.success('Assigned');
    } catch (e: any) {
      msg.error(e?.message || 'Assign failed');
    }
  };

  const columns = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 80 },
      { title: 'Name', dataIndex: 'name' },
      {
        title: 'Actions',
        width: 260,
        render: (_: any, r: Group) => (
          <Space>
            <Button
              size="small"
              onClick={() => {
                setCurrentGroup(r);
                setAssignOpen(true);
              }}
            >
              Assign Device
            </Button>
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
    <Card title="Groups" extra={<Button onClick={() => setOpen(true)}>New Group</Button>}>
      {ctx}
      <Table<Group> rowKey="id" loading={loading} dataSource={groups} columns={columns as any} pagination={false} />
      <Modal title="Create Group" open={open} onCancel={() => setOpen(false)} onOk={onCreate} okText="Create">
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title={`Assign Device to ${currentGroup?.name ?? ''}`} open={assignOpen} onCancel={() => setAssignOpen(false)} onOk={onAssign} okText="Assign">
        <Form form={assignForm} layout="vertical">
          <Form.Item name="device_id" label="Device" rules={[{ required: true }]}>
            <Select
              options={devices.map((d) => ({ value: d.id, label: `${d.name} (#${d.id})` }))}
              showSearch
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}

