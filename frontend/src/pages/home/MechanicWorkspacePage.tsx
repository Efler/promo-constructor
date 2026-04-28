import { Badge, Box, Button, Card, Group, List, Paper, Stack, Text, ThemeIcon, Title } from '@mantine/core'
import { IconArrowRight, IconCheck, IconSettings } from '@tabler/icons-react'
import { Link } from 'react-router-dom'

type MechanicWorkspacePageProps = {
  badge: string
  title: string
  description: string
  highlights: string[]
}

export function MechanicWorkspacePage({
  badge,
  title,
  description,
  highlights,
}: MechanicWorkspacePageProps) {
  return (
    <Stack gap="xl">
      <Paper
        p={{ base: 'lg', md: 'xl' }}
        radius="xl"
        shadow="md"
        style={{
          border: '1px solid rgba(113, 33, 93, 0.08)',
          background:
            'linear-gradient(135deg, rgba(255,255,255,0.96), rgba(248,241,250,0.92))',
        }}
      >
        <Group justify="space-between" align="start" gap="lg">
          <Box maw={760}>
            <Badge variant="light" color="brand" mb="md">
              {badge}
            </Badge>
            <Title order={2} c="dark.8">
              {title}
            </Title>
            <Text c="dimmed" mt="sm" size="lg">
              {description}
            </Text>
          </Box>

          <ThemeIcon size={56} radius="xl" color="brand">
            <IconSettings size={28} />
          </ThemeIcon>
        </Group>
      </Paper>

      <Group align="stretch" grow>
        <Paper
          p={{ base: 'lg', md: 'xl' }}
          radius="xl"
          shadow="sm"
          style={{ border: '1px solid rgba(113, 33, 93, 0.08)' }}
        >
          <Stack gap="md">
            <Title order={4}>Что уже готово</Title>
            <List
              spacing="md"
              icon={
                <ThemeIcon color="brand" variant="light" radius="xl" size={24}>
                  <IconCheck size={14} />
                </ThemeIcon>
              }
            >
              {highlights.map((item) => (
                <List.Item key={item}>{item}</List.Item>
              ))}
            </List>
          </Stack>
        </Paper>

        <Card
          p="xl"
          radius="xl"
          shadow="sm"
          style={{
            border: '1px dashed rgba(188, 61, 150, 0.4)',
            background:
              'linear-gradient(180deg, rgba(252,248,253,1) 0%, rgba(255,255,255,1) 100%)',
          }}
        >
          <Stack justify="space-between" h="100%">
            <div>
              <Text fw={700} size="lg">
                Область будущих форм
              </Text>
              <Text c="dimmed" mt="sm">
                Здесь появятся поля, таблицы и настройки механики на следующем этапе.
              </Text>
            </div>

            <Button
              component={Link}
              to="/app"
              variant="light"
              color="brand"
              rightSection={<IconArrowRight size={16} />}
            >
              Вернуться к выбору механик
            </Button>
          </Stack>
        </Card>
      </Group>
    </Stack>
  )
}
