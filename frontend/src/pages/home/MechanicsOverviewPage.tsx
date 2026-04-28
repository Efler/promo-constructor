import { Badge, Box, Button, Card, Group, Paper, SimpleGrid, Stack, Text, ThemeIcon, Title } from '@mantine/core'
import { IconArrowRight, IconChartBar, IconGift, IconTicket, IconTopologyStar3 } from '@tabler/icons-react'
import { Link } from 'react-router-dom'
import { mechanics } from './mechanics'

const iconMap = {
  promotions: IconChartBar,
  promocodes: IconTicket,
  bundles: IconGift,
}

export function MechanicsOverviewPage() {
  return (
    <Stack gap="xl">
      <Paper
        radius="xl"
        shadow="md"
        p={{ base: 'lg', md: 'xl' }}
        style={{
          border: '1px solid rgba(113, 33, 93, 0.08)',
          background:
            'linear-gradient(145deg, rgba(255,255,255,0.98), rgba(247,241,250,0.92))',
        }}
      >
        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="xl">
          <div>
            <Stack gap="md">
              <Badge variant="light" color="brand" w="fit-content">
                Seller workspace
              </Badge>
              <Title order={1} maw={720}>
                Выбери механику продвижения и продолжай настройку в едином конструкторе.
              </Title>
              <Text size="lg" c="dimmed" maw={680}>
                На этом этапе мы подготовили защищенный кабинет, базовую навигацию по
                механикам и пространство для дальнейшей реализации промо-логики.
              </Text>
            </Stack>
          </div>

          <div>
            <Paper
              radius="xl"
              p="lg"
              bg="brand.0"
              style={{ border: '1px solid rgba(188, 61, 150, 0.14)' }}
            >
              <Group align="start" wrap="nowrap">
                <ThemeIcon size={48} radius="xl" color="brand">
                  <IconTopologyStar3 size={26} />
                </ThemeIcon>
                <Box>
                  <Text fw={700}>Текущий фокус</Text>
                  <Text size="sm" c="dimmed" mt={6}>
                    Скелет приложения готов для следующего шага: auth, seller context и
                    интерфейс будущих механик.
                  </Text>
                </Box>
              </Group>
            </Paper>
          </div>
        </SimpleGrid>
      </Paper>

      <SimpleGrid cols={{ base: 1, md: 3 }} spacing="lg">
        {mechanics
          .filter((mechanic) => mechanic.key !== 'overview')
          .map((mechanic) => {
            const Icon = iconMap[mechanic.key as keyof typeof iconMap]

            return (
              <Card
                key={mechanic.key}
                radius="xl"
                padding="xl"
                shadow="sm"
                style={{
                  border: '1px solid rgba(113, 33, 93, 0.08)',
                  background: 'rgba(255, 255, 255, 0.96)',
                }}
              >
                <Stack justify="space-between" h="100%" gap="lg">
                  <div>
                    <ThemeIcon size={52} radius="xl" color="brand" variant="light">
                      <Icon size={24} />
                    </ThemeIcon>
                    <Group justify="space-between" mt="lg" align="start">
                      <Title order={3}>{mechanic.label}</Title>
                      <Badge variant="dot" color="brand">
                        Beta
                      </Badge>
                    </Group>
                    <Text c="dimmed" mt="sm">
                      {mechanic.description}
                    </Text>
                  </div>

                  <Button
                    component={Link}
                    to={mechanic.to}
                    variant="light"
                    color="brand"
                    rightSection={<IconArrowRight size={16} />}
                  >
                    Открыть механику
                  </Button>
                </Stack>
              </Card>
            )
          })}
      </SimpleGrid>
    </Stack>
  )
}
