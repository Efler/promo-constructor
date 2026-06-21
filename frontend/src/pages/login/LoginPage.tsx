import { Box, Button, Container, Paper, PasswordInput, Stack, Text, TextInput, Title } from '@mantine/core'
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
      username: (value) => (value.trim().length > 0 ? null : 'Укажи логин продавца'),
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
      let message = 'Проверь логин и пароль. Если ошибка повторится, попробуй позже.'

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
      } else if (error instanceof Error) {
        message = error.message
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
      <Box h={6} bg="brand.6" />

      <Container
        size={440}
        py={{ base: 48, sm: 72 }}
        style={{
          minHeight: 'calc(100vh - 6px)',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <Stack gap="xl" w="100%">
          <Stack gap={6} align="center">
            <Title order={1} ta="center" c="dark.8">
              Промо-навигатор
            </Title>
            <Text c="dimmed" ta="center">
              Вход в кабинет продавца
            </Text>
          </Stack>

          <Paper
            radius="xl"
            p={{ base: 'xl', sm: 36 }}
            shadow="md"
            style={{
              border: '1px solid rgba(154, 65, 254, 0.1)',
              background: 'rgba(255, 255, 255, 0.94)',
              backdropFilter: 'blur(16px)',
            }}
          >
            <form onSubmit={form.onSubmit(handleSubmit)}>
              <Stack gap="md">
                <TextInput
                  label="Логин"
                  placeholder="Введите логин"
                  size="md"
                  leftSection={<IconUserCircle size={18} />}
                  {...form.getInputProps('username')}
                />
                <PasswordInput
                  label="Пароль"
                  placeholder="Введите пароль"
                  size="md"
                  leftSection={<IconLock size={18} />}
                  {...form.getInputProps('password')}
                />
                <Button
                  type="submit"
                  size="md"
                  color="brand"
                  mt="xs"
                  rightSection={<IconArrowRight size={18} />}
                >
                  Войти
                </Button>
              </Stack>
            </form>
          </Paper>
        </Stack>
      </Container>
    </Box>
  )
}
