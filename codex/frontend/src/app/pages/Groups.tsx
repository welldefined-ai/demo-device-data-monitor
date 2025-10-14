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
  const [assigned, setAssigned] = useState<Device[]>([]);
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
                // load assigned devices for this group
                void (async () => {
                  try {
                    const ds = await api.get<Device[]>(`/groups/${r.id}/devices`);
                    setAssigned(ds);
                  } catch (e: any) {
                    msg.error(e?.message || 'Failed to load devices');
                  }
                })();
              }}
            >
              Manage Devices
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

      <Modal title={`Manage Devices in ${currentGroup?.name ?? ''}`} open={assignOpen} onCancel={() => setAssignOpen(false)} onOk={onAssign} okText="Assign">
        <Form form={assignForm} layout="vertical">
          <Form.Item name="device_id" label="Device" rules={[{ required: true }]}>
            <Select
              options={devices.map((d) => ({ value: d.id, label: `${d.name} (#${d.id})` }))}
              showSearch
            />
          </Form.Item>
        </Form>
        <div style={{ marginTop: 16 }}>
          <strong>Assigned Devices</strong>
          <div style={{ marginTop: 8 }}>
            {assigned.length === 0 ? (
              <div style={{ color: '#888' }}>No devices assigned.</div>
            ) : (
              assigned.map((d) => (
                <div key={d.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 0' }}>
                  <span>
                    {d.name} (#{d.id})
                  </span>
                  <Button
                    size="small"
                    onClick={async () => {
                      if (!currentGroup) return;
                      try {
                        await api.delete(`/groups/${currentGroup.id}/devices/${d.id}`);
                        setAssigned((prev) => prev.filter((x) => x.id !== d.id));
                        msg.success('Removed');
                      } catch (e: any) {
                        msg.error(e?.message || 'Remove failed');
                      }
                    }}
                  >
                    Remove
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>
      </Modal>
    </Card>
  );
}
