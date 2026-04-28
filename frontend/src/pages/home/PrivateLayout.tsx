import { AppShell, Avatar, Box, Button, Container, Divider, Group, Paper, Stack, Text, Title } from '@mantine/core'
import { IconLogout2 } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/auth/use-auth'
import { mechanics } from './mechanics'

export function PrivateLayout() {
  const { seller, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    try {
      await logout()
      notifications.show({
        color: 'brand',
        title: 'Сессия завершена',
        message: 'Ты вышел из seller workspace.',
      })
      navigate('/login')
    } catch {
      notifications.show({
        color: 'red',
        title: 'Не удалось выйти',
        message: 'Backend недоступен или сессия уже истекла.',
      })
    }
  }

  return (
    <AppShell
      padding="lg"
      header={{ height: 152 }}
      styles={{
        main: {
          background: 'transparent',
        },
      }}
    >
      <AppShell.Header withBorder={false} bg="transparent">
        <Box h={28} bg="#BC3D96" />

        <Container size="xl" py="lg">
          <Stack gap="md">
            <Group justify="space-between" align="start" gap="lg">
              <div>
                <Title order={2}>Промо конструктор</Title>
                <Text c="dimmed" mt={6}>
                  Конструктор механик продвижения для seller workflow
                </Text>
              </div>

              <Paper
                radius="xl"
                p="xs"
                shadow="sm"
                style={{ border: '1px solid rgba(113, 33, 93, 0.08)' }}
              >
                <Group gap="sm" wrap="nowrap">
                  <Avatar color="brand" radius="xl">
                    {seller?.display_name?.slice(0, 1).toUpperCase() ?? 'S'}
                  </Avatar>
                  <div>
                    <Text fw={700} size="sm">
                      {seller?.display_name}
                    </Text>
                    <Text size="xs" c="dimmed">
                      Seller login
                    </Text>
                  </div>
                  <Button
                    variant="subtle"
                    color="brand"
                    size="compact-sm"
                    onClick={handleLogout}
                    leftSection={<IconLogout2 size={16} />}
                  >
                    Выйти
                  </Button>
                </Group>
              </Paper>
            </Group>

            <Group gap="xs" wrap="wrap">
              {mechanics.map((mechanic) => (
                <NavLink
                  key={mechanic.key}
                  to={mechanic.to}
                  className={({ isActive }) =>
                    isActive ? 'mechanic-link mechanic-link--active' : 'mechanic-link'
                  }
                  end={mechanic.to === '/app'}
                >
                  {mechanic.label}
                  {mechanic.isBeta ? (
                    <Text span size="xs" c="brand.7">
                      Beta
                    </Text>
                  ) : null}
                </NavLink>
              ))}
            </Group>
          </Stack>
        </Container>

        <Divider color="rgba(113, 33, 93, 0.08)" />
      </AppShell.Header>

      <AppShell.Main>
        <Container size="xl" pb="xl">
          <Outlet />
        </Container>
      </AppShell.Main>
    </AppShell>
  )
}
