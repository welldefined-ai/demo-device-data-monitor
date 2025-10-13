import React, { useEffect, useMemo, useState } from 'react';
import { Button, Card, Form, Input, Modal, Select, Space, Table, Tag, message } from 'antd';
import { api } from '../../lib/api';
import { Role, User, useAuth } from '../../store/auth';

type NewUser = { username: string; password: string; role: Role };

export function UsersPage(): JSX.Element {
  const { user: current } = useAuth();
  const [data, setData] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm<NewUser>();
  const [msgApi, contextHolder] = message.useMessage();

  const load = async () => {
    try {
      setLoading(true);
      const users = await api.get<User[]>('/users');
      setData(users);
    } catch (e: any) {
      msgApi.error(e?.message ?? 'Failed to load users');
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
      await api.post<User>('/users', values);
      setModalOpen(false);
      form.resetFields();
      msgApi.success('User created');
      await load();
    } catch (e: any) {
      msgApi.error(e?.message || 'Failed to create user');
    }
  };

  const onDelete = async (id: number) => {
    try {
      await api.delete<void>(`/users/${id}`);
      msgApi.success('User deleted');
      await load();
    } catch (e: any) {
      msgApi.error(e?.message || 'Failed to delete user');
    }
  };

  const columns = useMemo(
    () => [
      { title: 'ID', dataIndex: 'id', width: 80 },
      { title: 'Username', dataIndex: 'username' },
      {
        title: 'Role',
        dataIndex: 'role',
        render: (role: Role) => <Tag color={role === 'owner' ? 'gold' : role === 'admin' ? 'geekblue' : 'green'}>{role}</Tag>,
      },
      {
        title: 'Actions',
        width: 160,
        render: (_: any, record: User) => (
          <Space>
            <Button danger size="small" disabled={record.role === 'owner'} onClick={() => onDelete(record.id)}>
              Delete
            </Button>
          </Space>
        ),
      },
    ],
    [],
  );

  return (
    <Card title="Users" extra={<Button type="primary" onClick={() => setModalOpen(true)}>New User</Button>}>
      {contextHolder}
      <Table<User> rowKey="id" columns={columns as any} dataSource={data} loading={loading} pagination={false} />

      <Modal
        title="Create User"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={onCreate}
        okText="Create"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="Username" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="role" label="Role" initialValue={current?.role === 'owner' ? 'admin' : 'viewer'} rules={[{ required: true }]}>
            <Select
              options={[
                ...(current?.role === 'owner' ? [{ value: 'admin', label: 'admin' }] : []),
                { value: 'viewer', label: 'viewer' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}

