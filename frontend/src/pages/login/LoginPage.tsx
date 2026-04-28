import { Box, Button, Container, Group, Paper, PasswordInput, Stack, Text, TextInput, Title } from '@mantine/core'
import { useForm } from '@mantine/form'
import { IconArrowRight, IconLock, IconUserCircle } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/auth/use-auth'
import { ApiError } from '../../shared/api/client'

type FormValues = {
  username: string
  password: string
}

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const form = useForm<FormValues>({
    initialValues: {
      username: '',
      password: '',
    },
    validate: {
      username: (value) => (value.trim().length > 0 ? null : 'Укажи логин селлера'),
      password: (value) => (value.trim().length > 0 ? null : 'Укажи пароль'),
    },
  })

  async function handleSubmit(values: FormValues) {
    try {
      const seller = await login(values)

      notifications.show({
        color: 'brand',
        title: 'Вход выполнен',
        message: `Добро пожаловать, ${seller.display_name}.`,
      })

      const nextPath = (location.state as { from?: string } | null)?.from ?? '/app'
      navigate(nextPath, { replace: true })
    } catch (error) {
      let message = 'Проверь логин, пароль и доступность backend API.'

      if (error instanceof ApiError) {
        const detail =
          typeof error.data === 'object' &&
          error.data !== null &&
          'detail' in error.data &&
          typeof error.data.detail === 'string'
            ? error.data.detail
            : null

        if (detail) {
          message = detail
        }
      }

      notifications.show({
        color: 'red',
        title: 'Не удалось войти',
        message,
      })
    }
  }

  return (
    <Box className="auth-page">
      <Box h={28} bg="#BC3D96" />

      <Container size={1180} py={{ base: 40, md: 72 }}>
        <Group align="stretch" gap="xl">
          <Paper
            flex={1}
            radius="xl"
            p={{ base: 'xl', md: 44 }}
            shadow="md"
            style={{
              border: '1px solid rgba(113, 33, 93, 0.08)',
              background: 'rgba(255, 255, 255, 0.88)',
              backdropFilter: 'blur(16px)',
            }}
          >
            <Stack gap="xl" justify="space-between" h="100%">
              <div>
                <Text c="brand.7" fw={700} tt="uppercase" size="sm" mb="md">
                  Promo Constructor
                </Text>
                <Title order={1} maw={520}>
                  Авторизуйся как seller, чтобы работать с механиками продвижения.
                </Title>
                <Text c="dimmed" size="lg" mt="md" maw={540}>
                  Доступ к механикам закрыт до входа. Seller-аккаунт теперь проверяется
                  через backend и PostgreSQL.
                </Text>
              </div>

              <Group gap="md" wrap="wrap">
                <Paper radius="xl" p="md" bg="brand.0">
                  <Text fw={600}>Промокоды</Text>
                  <Text size="sm" c="dimmed" mt={6}>
                    Скидки, лимиты, срок действия.
                  </Text>
                </Paper>
                <Paper radius="xl" p="md" bg="brand.0">
                  <Text fw={600}>Комплекты</Text>
                  <Text size="sm" c="dimmed" mt={6}>
                    Наборы товаров и бонусы.
                  </Text>
                </Paper>
                <Paper radius="xl" p="md" bg="brand.0">
                  <Text fw={600}>Акции</Text>
                  <Text size="sm" c="dimmed" mt={6}>
                    Кампании и правила показа.
                  </Text>
                </Paper>
              </Group>
            </Stack>
          </Paper>

          <Paper
            w={{ base: '100%', md: 430 }}
            radius="xl"
            p={{ base: 'xl', md: 36 }}
            shadow="md"
            style={{
              border: '1px solid rgba(113, 33, 93, 0.08)',
              background:
                'linear-gradient(180deg, rgba(255,255,255,0.97), rgba(249,244,250,0.95))',
            }}
          >
            <Stack gap="lg">
              <Group gap="sm">
                <IconUserCircle size={28} color="#BC3D96" />
                <div>
                  <Title order={3}>Seller login</Title>
                  <Text size="sm" c="dimmed">
                    Вход в защищенную часть конструктора
                  </Text>
                </div>
              </Group>

              <form onSubmit={form.onSubmit(handleSubmit)}>
                <Stack gap="md">
                  <TextInput
                    label="Логин"
                    placeholder="seller_roman"
                    leftSection={<IconUserCircle size={18} />}
                    {...form.getInputProps('username')}
                  />
                  <PasswordInput
                    label="Пароль"
                    placeholder="Введите пароль"
                    leftSection={<IconLock size={18} />}
                    {...form.getInputProps('password')}
                  />
                  <Button
                    type="submit"
                    size="md"
                    color="brand"
                    rightSection={<IconArrowRight size={18} />}
                  >
                    Войти в кабинет
                  </Button>
                </Stack>
              </form>

              <Text size="sm" c="dimmed">
                Для первого входа создай аккаунт через POST /api/v1/auth/register,
                затем используй обычный логин.
              </Text>
            </Stack>
          </Paper>
        </Group>
      </Container>
    </Box>
  )
}
