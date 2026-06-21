import { useMemo, useState } from 'react'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import {
  Alert,
  Badge,
  Box,
  Button,
  Checkbox,
  Group,
  Image,
  Paper,
  SegmentedControl,
  SimpleGrid,
  Skeleton,
  Stack,
  Text,
  TextInput,
  ThemeIcon,
  Title,
  UnstyledButton,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { notifications } from '@mantine/notifications'
import {
  IconAlertCircle,
  IconArrowLeft,
  IconCalendar,
  IconCheck,
  IconDiscount,
  IconInfoCircle,
  IconLock,
  IconPackage,
  IconSearch,
  IconSparkles,
} from '@tabler/icons-react'
import { useNavigate, useParams } from 'react-router-dom'
import productPlaceholder from '../../assets/product-placeholder.png'
import { useAuth } from '../../features/auth/use-auth'
import {
  formatProductMoney,
  type SellerProductPreviewItem,
  useSellerProductPreviewQuery,
} from '../../features/products/use-seller-product-preview'
import {
  getMarketplacePromotion,
  isPromotionJoinOpen,
  type MarketplacePromotion,
} from '../../features/promotions/catalog'
import { usePromotionParticipationsQuery } from '../../features/promotions/use-promotions'

dayjs.locale('ru')

type ProductFilter = 'eligible' | 'all'

type PromotionJoinFormValues = {
  discountPercent: string
  selectedProductIds: number[]
  acceptedPriceChange: boolean
}

type ProductEligibility = {
  eligible: boolean
  reasons: string[]
}

function getProductEligibility(
  product: SellerProductPreviewItem,
  promotion: MarketplacePromotion,
): ProductEligibility {
  const reasons: string[] = []

  if (!product.is_active) {
    reasons.push('Товар скрыт')
  }

  if (product.total_stock_qty < promotion.minimum_stock_qty) {
    reasons.push(`Остаток меньше ${promotion.minimum_stock_qty} шт.`)
  }

  if (
    promotion.eligible_parent_names !== null &&
    (!product.parent_name || !promotion.eligible_parent_names.includes(product.parent_name))
  ) {
    reasons.push('Категория не участвует')
  }

  return {
    eligible: reasons.length === 0,
    reasons,
  }
}

function getPromotionalPrice(product: SellerProductPreviewItem, discountPercent: number) {
  const currentPrice = Number(product.min_discounted_price ?? product.min_price)

  return Math.max(0, Math.round(currentPrice * (1 - discountPercent / 100)))
}

function PromotionProductCard({
  product,
  promotion,
  selected,
  targetDiscount,
  onToggle,
}: {
  product: SellerProductPreviewItem
  promotion: MarketplacePromotion
  selected: boolean
  targetDiscount: number
  onToggle: () => void
}) {
  const eligibility = getProductEligibility(product, promotion)
  const promotionalPrice = getPromotionalPrice(product, targetDiscount)

  return (
    <UnstyledButton
      type="button"
      onClick={eligibility.eligible ? onToggle : undefined}
      disabled={!eligibility.eligible}
      style={{ width: '100%', textAlign: 'left' }}
    >
      <Paper
        radius="xl"
        p="sm"
        shadow="sm"
        style={{
          opacity: eligibility.eligible ? 1 : 0.68,
          border: selected
            ? '1px solid rgba(154, 65, 254, 0.4)'
            : '1px solid rgba(154, 65, 254, 0.1)',
          background: selected
            ? 'linear-gradient(180deg, rgba(243,236,255,1) 0%, rgba(255,255,255,1) 100%)'
            : '#ffffff',
          boxShadow: selected ? '0 14px 28px rgba(154, 65, 254, 0.12)' : undefined,
          transition: 'all 160ms ease',
        }}
      >
        <Group align="start" wrap="nowrap" gap="md">
          <Box
            w={6}
            h={92}
            bg={selected ? 'brand.6' : eligibility.eligible ? 'gray.2' : 'red.2'}
            style={{ flexShrink: 0, borderRadius: 999 }}
          />

          <Image
            src={product.main_photo_url || productPlaceholder}
            alt={product.title}
            radius="lg"
            w={82}
            h={92}
            fit="cover"
          />

          <Stack gap={7} style={{ flex: 1, minWidth: 0 }}>
            <Group justify="space-between" align="start" gap="xs" wrap="nowrap">
              <div>
                <Text fw={700} lineClamp={2}>
                  {product.title}
                </Text>
                <Text size="xs" c="dimmed" mt={3}>
                  {[product.brand, product.parent_name].filter(Boolean).join(' · ')}
                </Text>
              </div>

              <ThemeIcon
                size={25}
                radius="xl"
                color={selected ? 'brand' : eligibility.eligible ? 'gray' : 'red'}
                variant={selected ? 'filled' : 'light'}
                style={{ flexShrink: 0 }}
              >
                {selected ? (
                  <IconCheck size={14} />
                ) : eligibility.eligible ? (
                  <IconPackage size={14} />
                ) : (
                  <IconLock size={13} />
                )}
              </ThemeIcon>
            </Group>

            <Group gap="xs">
              {eligibility.eligible ? (
                <Badge size="sm" color="teal" variant="light">
                  Подходит
                </Badge>
              ) : (
                eligibility.reasons.map((reason) => (
                  <Badge key={reason} size="sm" color="red" variant="light">
                    {reason}
                  </Badge>
                ))
              )}
            </Group>

            <Group justify="space-between" align="end" gap="sm">
              <div>
                <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
                  Сейчас
                </Text>
                <Text fw={700} size="sm">
                  {formatProductMoney(product.min_discounted_price ?? product.min_price)}
                </Text>
              </div>
              <div>
                <Text size="xs" c="dimmed" tt="uppercase" fw={700} ta="center">
                  В акции
                </Text>
                <Text fw={800} size="sm" c="brand" ta="center">
                  {formatProductMoney(String(promotionalPrice))}
                </Text>
              </div>
              <div>
                <Text size="xs" c="dimmed" tt="uppercase" fw={700} ta="right">
                  Остаток
                </Text>
                <Text fw={700} size="sm" ta="right">
                  {product.total_stock_qty} шт.
                </Text>
              </div>
            </Group>
          </Stack>
        </Group>
      </Paper>
    </UnstyledButton>
  )
}

function Requirement({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <Paper radius="lg" p="md" bg="gray.0">
      <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
        {label}
      </Text>
      <Text fw={750} mt={4}>
        {value}
      </Text>
    </Paper>
  )
}

export function PromotionJoinPage() {
  const { promotionId } = useParams()
  const promotion = getMarketplacePromotion(promotionId)
  const navigate = useNavigate()
  const { seller } = useAuth()
  const [search, setSearch] = useState('')
  const [productFilter, setProductFilter] = useState<ProductFilter>('eligible')
  const productsQuery = useSellerProductPreviewQuery({
    sellerId: seller?.id ?? null,
    enabled: promotion !== null,
  })
  const participationsQuery = usePromotionParticipationsQuery()

  const form = useForm<PromotionJoinFormValues>({
    initialValues: {
      discountPercent: String(promotion?.minimum_discount_percent ?? ''),
      selectedProductIds: [],
      acceptedPriceChange: false,
    },
    validate: {
      discountPercent: (value) => {
        if (!promotion) {
          return null
        }

        if (!/^\d+$/.test(value)) {
          return 'Укажите скидку целым числом.'
        }

        const numericValue = Number(value)
        if (
          numericValue < promotion.minimum_discount_percent ||
          numericValue > 99
        ) {
          return `Допустимая скидка — от ${promotion.minimum_discount_percent}% до 99%.`
        }

        return null
      },
      selectedProductIds: (value) => {
        if (!promotion) {
          return null
        }

        if (value.length < promotion.minimum_products) {
          return `Для участия выберите минимум ${promotion.minimum_products} товар(а).`
        }

        return null
      },
      acceptedPriceChange: (value) =>
        value ? null : 'Подтвердите применение акционных цен.',
    },
  })

  const products = useMemo(() => productsQuery.data ?? [], [productsQuery.data])
  const normalizedSearch = search.trim().toLocaleLowerCase('ru-RU')
  const targetDiscount = Number(form.values.discountPercent) || 0
  const eligibleProducts = promotion
    ? products.filter((product) => getProductEligibility(product, promotion).eligible)
    : []
  const visibleProducts = useMemo(() => {
    if (!promotion) {
      return []
    }

    return products.filter((product) => {
      const eligibility = getProductEligibility(product, promotion)
      const matchesFilter = productFilter === 'all' || eligibility.eligible
      const searchableText = [
        product.title,
        product.brand,
        product.subject_name,
        product.parent_name,
      ]
        .filter(Boolean)
        .join(' ')
        .toLocaleLowerCase('ru-RU')

      return matchesFilter && (!normalizedSearch || searchableText.includes(normalizedSearch))
    })
  }, [normalizedSearch, productFilter, products, promotion])

  if (!promotion) {
    return (
      <Paper
        radius="xl"
        p="xl"
        shadow="sm"
        style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
      >
        <Stack align="center" gap="md">
          <ThemeIcon size={54} radius="xl" variant="light" color="red">
            <IconAlertCircle size={25} />
          </ThemeIcon>
          <Title order={2}>Акция не найдена</Title>
          <Text c="dimmed" ta="center">
            Возможно, ссылка устарела или кампания больше недоступна.
          </Text>
          <Button radius="xl" onClick={() => navigate('/app/promotions')}>
            Вернуться к календарю
          </Button>
        </Stack>
      </Paper>
    )
  }

  const joinOpen = isPromotionJoinOpen(promotion)
  const alreadyParticipating = (participationsQuery.data?.items ?? []).some(
    (participation) =>
      participation.promotion_id === promotion.id &&
      participation.status !== 'completed',
  )
  const selectedProducts = products.filter((product) =>
    form.values.selectedProductIds.includes(product.id),
  )

  function toggleProduct(productId: number) {
    const nextValue = form.values.selectedProductIds.includes(productId)
      ? form.values.selectedProductIds.filter((id) => id !== productId)
      : [...form.values.selectedProductIds, productId]

    form.setFieldValue('selectedProductIds', nextValue)
    form.clearFieldError('selectedProductIds')
  }

  function handleSubmit() {
    if (!joinOpen || alreadyParticipating) {
      return
    }

    notifications.show({
      color: 'brand',
      title: 'Настройки участия готовы',
      message:
        'Товары и скидка проверены. Сохранение участия будет подключено на backend-этапе.',
    })
  }

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <Stack gap="xl" maw={1120} mx="auto">
        <Group>
          <Button
            type="button"
            variant="subtle"
            color="gray"
            leftSection={<IconArrowLeft size={17} />}
            onClick={() => navigate('/app/promotions')}
          >
            К календарю акций
          </Button>
        </Group>

        <Paper
          radius="xl"
          p={{ base: 'lg', md: 'xl' }}
          shadow="md"
          style={{
            border: `1px solid var(--mantine-color-${promotion.tone}-2)`,
            background: `linear-gradient(145deg, var(--mantine-color-${promotion.tone}-0), #ffffff 72%)`,
          }}
        >
          <Stack gap="lg">
            <Group justify="space-between" align="start" gap="lg">
              <div>
                <Badge color={promotion.tone} variant="light" mb="md">
                  Присоединение к акции
                </Badge>
                <Title order={1}>{promotion.title}</Title>
                <Text c="dimmed" mt="sm" maw={760}>
                  {promotion.short_description}
                </Text>
              </div>
              <ThemeIcon size={54} radius="xl" color={promotion.tone}>
                <IconDiscount size={25} />
              </ThemeIcon>
            </Group>

            <Group gap="xl">
              <Group gap="xs">
                <IconCalendar size={18} color="var(--mantine-color-brand-6)" />
                <Text fw={650}>
                  {dayjs(promotion.starts_on).format('D MMMM')} —{' '}
                  {dayjs(promotion.ends_on).format('D MMMM YYYY')}
                </Text>
              </Group>
              <Text size="sm" c="dimmed">
                Вступление до {dayjs(promotion.join_deadline).format('D MMMM YYYY')}
              </Text>
            </Group>

            {!joinOpen ? (
              <Alert
                color="orange"
                variant="light"
                radius="lg"
                icon={<IconAlertCircle size={18} />}
              >
                Приём новых товаров в эту акцию уже завершён.
              </Alert>
            ) : null}

            {alreadyParticipating ? (
              <Alert color="teal" variant="light" radius="lg" icon={<IconCheck size={18} />}>
                Вы уже участвуете в этой акции. Текущие настройки загружены с backend.
              </Alert>
            ) : null}
          </Stack>
        </Paper>

        <Paper
          radius="xl"
          p={{ base: 'lg', md: 'xl' }}
          shadow="sm"
          style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
        >
          <Stack gap="lg">
            <div>
              <Title order={3}>Условия маркетплейса</Title>
              <Text c="dimmed" mt="sm">
                Товары должны соответствовать всем требованиям на момент вступления.
              </Text>
            </div>

            <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="sm">
              <Requirement
                label="Минимальная скидка"
                value={`${promotion.minimum_discount_percent}%`}
              />
              <Requirement
                label="Остаток товара"
                value={`от ${promotion.minimum_stock_qty} шт.`}
              />
              <Requirement
                label="Количество товаров"
                value={`от ${promotion.minimum_products}`}
              />
              <Requirement
                label="Категории"
                value={
                  promotion.eligible_parent_names?.join(', ') ?? 'Весь ассортимент'
                }
              />
            </SimpleGrid>

            <SimpleGrid cols={{ base: 1, md: 2 }} spacing="sm">
              {promotion.benefits.slice(0, 2).map((benefit) => (
                <Paper
                  key={benefit}
                  p="sm"
                  radius="lg"
                  bg={`${promotion.tone}.0`}
                >
                  <Group gap="sm" wrap="nowrap" align="start">
                    <ThemeIcon
                      size={28}
                      radius="xl"
                      color={promotion.tone}
                      variant="light"
                      style={{ flexShrink: 0 }}
                    >
                      <IconSparkles size={15} />
                    </ThemeIcon>
                    <Text size="sm">{benefit}</Text>
                  </Group>
                </Paper>
              ))}
            </SimpleGrid>
          </Stack>
        </Paper>

        <Paper
          radius="xl"
          p={{ base: 'lg', md: 'xl' }}
          shadow="sm"
          style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
        >
          <Stack gap="lg">
            <div>
              <Title order={3}>Акционная скидка</Title>
              <Text c="dimmed" mt="sm">
                Одна дополнительная скидка применяется ко всем выбранным товарам от
                их текущей цены.
              </Text>
            </div>

            <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
              <TextInput
                label="Скидка, %"
                placeholder={String(promotion.minimum_discount_percent)}
                inputMode="numeric"
                leftSection={<IconDiscount size={16} />}
                value={form.values.discountPercent}
                error={form.errors.discountPercent}
                onBlur={() => form.validateField('discountPercent')}
                onChange={(event) => {
                  form.clearFieldError('discountPercent')
                  form.setFieldValue(
                    'discountPercent',
                    event.currentTarget.value.replace(/[^\d]/g, ''),
                  )
                }}
              />

              <Alert
                color="brand"
                variant="light"
                radius="lg"
                icon={<IconInfoCircle size={18} />}
              >
                Минимум для этой акции — {promotion.minimum_discount_percent}%.
                В карточках товаров сразу показана цена после применения выбранной
                дополнительной скидки.
              </Alert>
            </SimpleGrid>
          </Stack>
        </Paper>

        <Paper
          radius="xl"
          p={{ base: 'lg', md: 'xl' }}
          shadow="sm"
          style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
        >
          <Stack gap="lg">
            <Group justify="space-between" align="end" gap="md">
              <div>
                <Title order={3}>Товары продавца</Title>
                <Text c="dimmed" mt="sm">
                  Подходят {eligibleProducts.length} из {products.length} товаров.
                </Text>
              </div>
              <Badge color="brand" variant="light" size="lg">
                Выбрано: {form.values.selectedProductIds.length}
              </Badge>
            </Group>

            <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
              <TextInput
                placeholder="Название, бренд или категория"
                leftSection={<IconSearch size={16} />}
                value={search}
                onChange={(event) => setSearch(event.currentTarget.value)}
              />
              <SegmentedControl
                fullWidth
                value={productFilter}
                onChange={(value) => setProductFilter(value as ProductFilter)}
                data={[
                  { label: 'Только подходящие', value: 'eligible' },
                  { label: 'Все товары', value: 'all' },
                ]}
              />
            </SimpleGrid>

            {form.errors.selectedProductIds ? (
              <Text size="sm" c="red" fw={600}>
                {form.errors.selectedProductIds}
              </Text>
            ) : null}

            {!productsQuery.isLoading &&
            !productsQuery.isError &&
            products.length > 0 &&
            eligibleProducts.length < promotion.minimum_products ? (
              <Alert
                radius="lg"
                color="orange"
                variant="light"
                icon={<IconAlertCircle size={18} />}
              >
                Сейчас требованиям соответствуют только {eligibleProducts.length} товар(а),
                а для участия нужно минимум {promotion.minimum_products}. Пополните
                остатки или выберите другую акцию.
              </Alert>
            ) : null}

            {productsQuery.isLoading ? (
              <Stack gap="sm">
                {[1, 2, 3, 4].map((item) => (
                  <Paper
                    key={item}
                    p="sm"
                    radius="xl"
                    shadow="sm"
                    style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
                  >
                    <Group align="start" wrap="nowrap" gap="md">
                      <Skeleton height={92} width={6} radius="xl" />
                      <Skeleton height={92} width={82} radius="lg" />
                      <Stack gap="sm" style={{ flex: 1 }}>
                        <Skeleton height={18} radius="md" />
                        <Skeleton height={14} width="70%" radius="md" />
                        <Skeleton height={28} width="55%" radius="md" />
                      </Stack>
                    </Group>
                  </Paper>
                ))}
              </Stack>
            ) : null}

            {!productsQuery.isLoading && productsQuery.isError ? (
              <Alert
                radius="lg"
                color="red"
                variant="light"
                icon={<IconAlertCircle size={18} />}
              >
                Не удалось загрузить товары продавца. Попробуйте обновить страницу.
              </Alert>
            ) : null}

            {!productsQuery.isLoading &&
            !productsQuery.isError &&
            products.length === 0 ? (
              <Paper
                radius="xl"
                p="xl"
                style={{ border: '1px dashed rgba(154, 65, 254, 0.24)' }}
              >
                <Stack align="center" gap="sm">
                  <ThemeIcon size={50} radius="xl" variant="light" color="brand">
                    <IconPackage size={23} />
                  </ThemeIcon>
                  <Text fw={700}>Товары не найдены</Text>
                  <Text size="sm" c="dimmed" ta="center">
                    В ассортименте продавца пока нет доступных карточек.
                  </Text>
                </Stack>
              </Paper>
            ) : null}

            {!productsQuery.isLoading &&
            !productsQuery.isError &&
            products.length > 0 &&
            visibleProducts.length === 0 ? (
              <Paper
                radius="xl"
                p="xl"
                style={{ border: '1px dashed rgba(154, 65, 254, 0.24)' }}
              >
                <Stack align="center" gap="sm">
                  <ThemeIcon size={50} radius="xl" variant="light" color="orange">
                    <IconSearch size={23} />
                  </ThemeIcon>
                  <Text fw={700}>По фильтрам ничего не найдено</Text>
                  <Text size="sm" c="dimmed" ta="center">
                    Измените поиск или включите отображение всех товаров.
                  </Text>
                </Stack>
              </Paper>
            ) : null}

            {!productsQuery.isLoading &&
            !productsQuery.isError &&
            visibleProducts.length > 0 ? (
              <Stack
                gap="sm"
                style={{ maxHeight: 650, overflowY: 'auto', paddingRight: 4 }}
              >
                {visibleProducts.map((product) => (
                  <PromotionProductCard
                    key={product.id}
                    product={product}
                    promotion={promotion}
                    selected={form.values.selectedProductIds.includes(product.id)}
                    targetDiscount={targetDiscount}
                    onToggle={() => toggleProduct(product.id)}
                  />
                ))}
              </Stack>
            ) : null}
          </Stack>
        </Paper>

        <Paper
          radius="xl"
          p={{ base: 'lg', md: 'xl' }}
          shadow="sm"
          style={{ border: '1px solid rgba(154, 65, 254, 0.1)' }}
        >
          <Stack gap="lg">
            <Group align="start" gap="md" wrap="nowrap">
              <ThemeIcon size={48} radius="xl" variant="light" color="brand">
                <IconCheck size={22} />
              </ThemeIcon>
              <div>
                <Title order={3}>Итоговые настройки</Title>
                <Text c="dimmed" mt={5}>
                  {selectedProducts.length} товар(а), скидка {targetDiscount || 0}%,
                  период с {dayjs(promotion.starts_on).format('D MMMM')} по{' '}
                  {dayjs(promotion.ends_on).format('D MMMM')}.
                </Text>
              </div>
            </Group>

            <Checkbox
              label="Я подтверждаю применение рассчитанных акционных цен к выбранным товарам на весь период акции."
              color="brand"
              {...form.getInputProps('acceptedPriceChange', { type: 'checkbox' })}
            />
            {form.errors.acceptedPriceChange ? (
              <Text size="sm" c="red" fw={600}>
                {form.errors.acceptedPriceChange}
              </Text>
            ) : null}

            <Alert
              radius="lg"
              color="blue"
              variant="light"
              icon={<IconInfoCircle size={18} />}
            >
              На этом frontend-этапе кнопка проверяет настройки, но не сохраняет участие:
              POST-контракт и таблицы будут добавлены вместе с backend-реализацией.
            </Alert>
          </Stack>
        </Paper>

        <Button
          type="submit"
          size="lg"
          variant="gradient"
          gradient={{ from: 'brand.5', to: 'brand.7', deg: 90 }}
          radius="xl"
          fullWidth
          disabled={!joinOpen || alreadyParticipating}
          styles={{
            root: {
              minHeight: 58,
              boxShadow: '0 16px 30px rgba(154, 65, 254, 0.18)',
            },
          }}
        >
          Проверить и подготовить участие
        </Button>
      </Stack>
    </form>
  )
}
