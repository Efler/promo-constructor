import { useMemo, useRef, useState } from 'react'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import {
  Alert,
  Badge,
  Box,
  Button,
  Group,
  Loader,
  Paper,
  SimpleGrid,
  Stack,
  Tabs,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core'
import { DatePicker } from '@mantine/dates'
import {
  IconAlertCircle,
  IconArrowRight,
  IconCalendar,
  IconChartBar,
  IconCheck,
  IconClock,
  IconDiscount,
  IconListCheck,
  IconPackage,
  IconSparkles,
} from '@tabler/icons-react'
import { useNavigate } from 'react-router-dom'
import {
  getMarketplacePromotionStatus,
  isDateInsidePromotion,
  isPromotionJoinOpen,
  marketplacePromotions,
  type MarketplacePromotion,
  type MarketplacePromotionStatus,
} from '../../features/promotions/catalog'
import { usePromotionParticipationsQuery } from '../../features/promotions/use-promotions'

dayjs.locale('ru')

const statusLabels: Record<MarketplacePromotionStatus, string> = {
  active: 'Идёт сейчас',
  ending_soon: 'Скоро завершится',
  upcoming: 'Скоро начнётся',
  closed: 'Завершена',
}

const statusColors: Record<MarketplacePromotionStatus, string> = {
  active: 'teal',
  ending_soon: 'orange',
  upcoming: 'brand',
  closed: 'gray',
}

function formatPeriod(promotion: MarketplacePromotion) {
  return `${dayjs(promotion.starts_on).format('D MMMM')} — ${dayjs(promotion.ends_on).format(
    'D MMMM',
  )}`
}

function getJoinDeadlineLabel(promotion: MarketplacePromotion) {
  const daysLeft = dayjs(promotion.join_deadline).diff(dayjs().startOf('day'), 'day')

  if (daysLeft < 0) {
    return 'Приём заявок завершён'
  }

  if (daysLeft === 0) {
    return 'Последний день для вступления'
  }

  return `Вступить до ${dayjs(promotion.join_deadline).format('D MMMM')}`
}

function PromotionCard({
  promotion,
  participating,
  onJoin,
}: {
  promotion: MarketplacePromotion
  participating: boolean
  onJoin: () => void
}) {
  const status = getMarketplacePromotionStatus(promotion)
  const joinOpen = isPromotionJoinOpen(promotion)
  const categories =
    promotion.eligible_parent_names === null
      ? 'Все категории'
      : promotion.eligible_parent_names.join(', ')

  return (
    <Paper
      radius="xl"
      p="lg"
      shadow="sm"
      style={{
        height: '100%',
        border: `1px solid var(--mantine-color-${promotion.tone}-2)`,
        background: promotion.featured
          ? `linear-gradient(145deg, var(--mantine-color-${promotion.tone}-0), #ffffff 70%)`
          : 'rgba(255, 255, 255, 0.98)',
      }}
    >
      <Stack gap="md" justify="space-between" h="100%">
        <Stack gap="md">
          <Group justify="space-between" align="start" gap="sm">
            <Badge color={statusColors[status]} variant="light">
              {statusLabels[status]}
            </Badge>

            {participating ? (
              <ThemeIcon color="teal" variant="light" radius="xl">
                <IconCheck size={16} />
              </ThemeIcon>
            ) : null}
          </Group>

          <div>
            <Title order={3}>{promotion.title}</Title>
            <Text c="dimmed" mt={8} size="sm">
              {promotion.short_description}
            </Text>
          </div>

          <Group gap="lg">
            <Group gap={7} wrap="nowrap">
              <IconCalendar size={17} color="var(--mantine-color-brand-6)" />
              <Text size="sm" fw={650}>
                {formatPeriod(promotion)}
              </Text>
            </Group>
            <Group gap={7} wrap="nowrap">
              <IconClock size={17} color="var(--mantine-color-gray-6)" />
              <Text size="sm">{getJoinDeadlineLabel(promotion)}</Text>
            </Group>
          </Group>

          <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="sm">
            <Paper radius="lg" p="sm" bg="gray.0">
              <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
                Скидка от
              </Text>
              <Text fw={750} mt={3}>
                {promotion.minimum_discount_percent}%
              </Text>
            </Paper>
            <Paper radius="lg" p="sm" bg="gray.0">
              <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
                Остаток от
              </Text>
              <Text fw={750} mt={3}>
                {promotion.minimum_stock_qty} шт.
              </Text>
            </Paper>
            <Paper radius="lg" p="sm" bg="gray.0">
              <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
                Товаров от
              </Text>
              <Text fw={750} mt={3}>
                {promotion.minimum_products}
              </Text>
            </Paper>
          </SimpleGrid>

          <div>
            <Text size="sm" fw={700}>
              Категории
            </Text>
            <Text size="sm" c="dimmed" mt={3}>
              {categories}
            </Text>
          </div>

          <Stack gap={7}>
            {promotion.benefits.slice(0, 2).map((benefit) => (
              <Group key={benefit} gap="xs" wrap="nowrap" align="start">
                <ThemeIcon
                  size={20}
                  radius="xl"
                  variant="light"
                  color={promotion.tone}
                  mt={1}
                >
                  <IconSparkles size={12} />
                </ThemeIcon>
                <Text size="sm">{benefit}</Text>
              </Group>
            ))}
          </Stack>
        </Stack>

        <Button
          radius="xl"
          variant={participating ? 'light' : 'filled'}
          color={participating ? 'teal' : 'brand'}
          rightSection={!participating && joinOpen ? <IconArrowRight size={16} /> : null}
          disabled={!joinOpen && !participating}
          onClick={onJoin}
        >
          {participating
            ? 'Вы уже участвуете'
            : joinOpen
              ? 'Выбрать товары'
              : 'Вступление закрыто'}
        </Button>
      </Stack>
    </Paper>
  )
}

function MetricCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: number
  color: string
}) {
  return (
    <Paper radius="xl" p="lg" shadow="sm" style={{ border: '1px solid #ececf0' }}>
      <Group gap="md" wrap="nowrap">
        <ThemeIcon size={44} radius="xl" color={color} variant="light">
          {icon}
        </ThemeIcon>
        <div>
          <Text size="xs" tt="uppercase" fw={700} c="dimmed">
            {label}
          </Text>
          <Text size="xl" fw={800} mt={2}>
            {value}
          </Text>
        </div>
      </Group>
    </Paper>
  )
}

export function PromotionDashboardPage() {
  const navigate = useNavigate()
  const catalogRef = useRef<HTMLDivElement>(null)
  const [activeTab, setActiveTab] = useState<string | null>('available')
  const [selectedDate, setSelectedDate] = useState<string | null>(
    dayjs().format('YYYY-MM-DD'),
  )
  const participationsQuery = usePromotionParticipationsQuery()
  const participations = participationsQuery.data?.items ?? []
  const currentParticipations = participations.filter(
    (participation) => participation.status !== 'completed',
  )
  const participationPromotionIds = new Set(
    currentParticipations.map((participation) => participation.promotion_id),
  )

  const visiblePromotions = useMemo(() => {
    if (!selectedDate) {
      return marketplacePromotions
    }

    return marketplacePromotions.filter((promotion) =>
      isDateInsidePromotion(selectedDate, promotion),
    )
  }, [selectedDate])

  const availablePromotionCount = marketplacePromotions.filter(isPromotionJoinOpen).length

  const participatingProductsCount = new Set(
    currentParticipations.flatMap((participation) => participation.selected_product_ids),
  ).size

  function handleOpenCatalog() {
    setActiveTab('available')
    window.requestAnimationFrame(() => {
      catalogRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }

  return (
    <Stack gap="xl">
      <Paper
        radius="xl"
        p={{ base: 'lg', md: 'xl' }}
        shadow="md"
        style={{
          border: '1px solid rgba(154, 65, 254, 0.1)',
          background:
            'linear-gradient(145deg, rgba(255,255,255,0.98), rgba(244,239,252,0.96))',
        }}
      >
        <Group justify="space-between" align="start" gap="xl">
          <div>
            <Badge variant="light" color="brand" mb="md">
              Акции маркетплейса
            </Badge>
            <Title order={1}>Календарь акций</Title>
            <Text c="dimmed" mt="sm" maw={760}>
              Выбирайте готовые кампании маркетплейса, добавляйте подходящие товары и
              получайте дополнительное продвижение товаров.
            </Text>
          </div>

          <Button
            size="md"
            radius="xl"
            leftSection={<IconCalendar size={18} />}
            onClick={handleOpenCatalog}
          >
            Выбрать акцию
          </Button>
        </Group>
      </Paper>

      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="lg">
        <MetricCard
          icon={<IconChartBar size={21} />}
          label="Доступно акций"
          value={availablePromotionCount}
          color="brand"
        />
        <MetricCard
          icon={<IconListCheck size={21} />}
          label="Активных участий"
          value={currentParticipations.length}
          color="teal"
        />
        <MetricCard
          icon={<IconPackage size={21} />}
          label="Товаров в акциях"
          value={participatingProductsCount}
          color="orange"
        />
      </SimpleGrid>

      <Box ref={catalogRef} style={{ scrollMarginTop: 24 }}>
        <Tabs value={activeTab} onChange={setActiveTab} color="brand" radius="xl">
          <Tabs.List mb="lg">
            <Tabs.Tab value="available" leftSection={<IconDiscount size={16} />}>
              Доступные акции
            </Tabs.Tab>
            <Tabs.Tab value="mine" leftSection={<IconListCheck size={16} />}>
              Мои участия
              {participations.length > 0 ? (
                <Badge ml="xs" size="xs" circle color="brand">
                  {participations.length}
                </Badge>
              ) : null}
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="available">
            <SimpleGrid
              cols={{ base: 1, lg: 2 }}
              spacing="xl"
              style={{ alignItems: 'start' }}
            >
              <Paper
                radius="xl"
                p={{ base: 'md', md: 'lg' }}
                shadow="sm"
                style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
              >
                <Stack gap="md">
                  <div>
                    <Title order={3}>Акции по датам</Title>
                    <Text size="sm" c="dimmed" mt={6}>
                      Нажмите на дату, чтобы увидеть акции, которые проходят в этот день.
                    </Text>
                  </div>

                  <DatePicker
                    value={selectedDate}
                    onChange={setSelectedDate}
                    locale="ru"
                    firstDayOfWeek={1}
                    fullWidth
                    highlightToday
                    size="md"
                    renderDay={(date) => {
                      const promotionsOnDate = marketplacePromotions.filter((promotion) =>
                        isDateInsidePromotion(date, promotion),
                      )

                      return (
                        <Stack gap={2} align="center">
                          <Text span inherit>
                            {dayjs(date).date()}
                          </Text>
                          {promotionsOnDate.length > 0 ? (
                            <Group gap={2}>
                              {promotionsOnDate.slice(0, 3).map((promotion) => (
                                <Box
                                  key={promotion.id}
                                  w={4}
                                  h={4}
                                  bg={`${promotion.tone}.6`}
                                  style={{ borderRadius: 999 }}
                                />
                              ))}
                            </Group>
                          ) : null}
                        </Stack>
                      )
                    }}
                  />

                  {selectedDate ? (
                    <Button variant="subtle" radius="xl" onClick={() => setSelectedDate(null)}>
                      Показать все акции
                    </Button>
                  ) : null}

                  <Paper radius="lg" p="md" bg="brand.0">
                    <Text size="sm" fw={700}>
                      Как это работает
                    </Text>
                    <Text size="sm" c="dimmed" mt={5}>
                      Маркетплейс определяет сроки и минимальные условия. Вы выбираете
                      подходящие товары и подтверждаете скидку.
                    </Text>
                  </Paper>
                </Stack>
              </Paper>

              <Stack gap="md">
                <Group justify="space-between" align="end">
                  <div>
                    <Title order={3}>
                      {selectedDate
                        ? `Акции на ${dayjs(selectedDate).format('D MMMM')}`
                        : 'Все доступные акции'}
                    </Title>
                    <Text size="sm" c="dimmed" mt={5}>
                      Найдено: {visiblePromotions.length}
                    </Text>
                  </div>
                </Group>

                {visiblePromotions.length > 0 ? (
                  <SimpleGrid cols={{ base: 1, xl: 2 }} spacing="md">
                    {visiblePromotions.map((promotion) => (
                      <PromotionCard
                        key={promotion.id}
                        promotion={promotion}
                        participating={participationPromotionIds.has(promotion.id)}
                        onJoin={() => {
                          if (!participationPromotionIds.has(promotion.id)) {
                            navigate(`/app/promotions/${promotion.id}/join`)
                          } else {
                            setActiveTab('mine')
                          }
                        }}
                      />
                    ))}
                  </SimpleGrid>
                ) : (
                  <Paper
                    radius="xl"
                    p="xl"
                    style={{ border: '1px dashed rgba(154, 65, 254, 0.24)' }}
                  >
                    <Stack align="center" gap="sm">
                      <ThemeIcon size={50} radius="xl" variant="light" color="brand">
                        <IconCalendar size={23} />
                      </ThemeIcon>
                      <Text fw={700}>На эту дату акций нет</Text>
                      <Text size="sm" c="dimmed" ta="center">
                        Выберите другой день или вернитесь к полному списку.
                      </Text>
                    </Stack>
                  </Paper>
                )}
              </Stack>
            </SimpleGrid>
          </Tabs.Panel>

          <Tabs.Panel value="mine">
            <Paper
              radius="xl"
              p={{ base: 'lg', md: 'xl' }}
              shadow="sm"
              style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
            >
              <Stack gap="lg">
                <div>
                  <Title order={3}>Акции, в которых вы участвуете</Title>
                  <Text c="dimmed" mt="sm">
                    Данные загружаются из текущего backend-модуля `/promotions`.
                  </Text>
                </div>

                {participationsQuery.isLoading ? (
                  <Group justify="center" py="xl">
                    <Loader color="brand" />
                  </Group>
                ) : null}

                {!participationsQuery.isLoading && participationsQuery.isError ? (
                  <Alert
                    radius="lg"
                    color="red"
                    variant="light"
                    icon={<IconAlertCircle size={18} />}
                    title="Не удалось загрузить участия"
                  >
                    Каталог акций доступен, но backend не вернул данные продавца.
                  </Alert>
                ) : null}

                {!participationsQuery.isLoading &&
                !participationsQuery.isError &&
                participations.length === 0 ? (
                  <Paper
                    radius="xl"
                    p="xl"
                    style={{ border: '1px dashed rgba(154, 65, 254, 0.24)' }}
                  >
                    <Stack align="center" gap="sm">
                      <ThemeIcon size={52} radius="xl" variant="light" color="brand">
                        <IconListCheck size={24} />
                      </ThemeIcon>
                      <Text fw={700}>Вы пока не участвуете в акциях</Text>
                      <Text size="sm" c="dimmed" ta="center" maw={560}>
                        Выберите подходящую кампанию и подготовьте товары. Сохранение
                        участия появится на следующем backend-этапе.
                      </Text>
                      <Button radius="xl" mt="sm" onClick={handleOpenCatalog}>
                        Посмотреть доступные акции
                      </Button>
                    </Stack>
                  </Paper>
                ) : null}

                {!participationsQuery.isLoading &&
                !participationsQuery.isError &&
                participations.length > 0 ? (
                  <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                    {participations.map((participation) => (
                      <Paper
                        key={participation.id}
                        radius="xl"
                        p="lg"
                        bg="gray.0"
                        style={{ border: '1px solid #ececf0' }}
                      >
                        <Stack gap="sm">
                          <Group justify="space-between">
                            <Badge
                              color={participation.status === 'active' ? 'teal' : 'brand'}
                              variant="light"
                            >
                              {participation.status === 'active'
                                ? 'Активна'
                                : participation.status === 'scheduled'
                                  ? 'Запланирована'
                                  : 'Завершена'}
                            </Badge>
                            <Text size="xs" c="dimmed">
                              с {dayjs(participation.joined_at).format('D MMMM YYYY')}
                            </Text>
                          </Group>
                          <Title order={4}>{participation.promotion_title}</Title>
                          <Group gap="lg">
                            <Text size="sm">
                              Товаров: <b>{participation.selected_product_ids.length}</b>
                            </Text>
                            <Text size="sm">
                              Скидка: <b>{participation.discount_percent}%</b>
                            </Text>
                          </Group>
                        </Stack>
                      </Paper>
                    ))}
                  </SimpleGrid>
                ) : null}
              </Stack>
            </Paper>
          </Tabs.Panel>
        </Tabs>
      </Box>
    </Stack>
  )
}
