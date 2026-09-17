import { SITE } from '../config';
import { canonical } from './routes';

export function websiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: SITE.name,
    alternateName: SITE.masterTitle,
    url: `${SITE.baseUrl}/`,
    description: SITE.description,
    inLanguage: 'en',
    publisher: { '@type': 'Organization', name: SITE.name, url: `${SITE.baseUrl}/` },
  };
}

export function organizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE.name,
    url: `${SITE.baseUrl}/`,
    description: SITE.description,
    slogan: SITE.tagline,
    email: SITE.email,
  };
}

export function breadcrumbSchema(trail: { name: string; path: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: trail.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: canonical(item.path),
    })),
  };
}

export function itemListSchema(
  name: string,
  path: string,
  items: { name: string; path: string }[],
) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name,
    url: canonical(path),
    numberOfItems: items.length,
    itemListOrder: 'https://schema.org/ItemListOrderAscending',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      url: canonical(item.path),
    })),
  };
}

export function articleSchema(input: {
  headline: string;
  description: string;
  path: string;
  section: string;
  keywords: string[];
  dateModified?: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: input.headline,
    description: input.description,
    url: canonical(input.path),
    mainEntityOfPage: { '@type': 'WebPage', '@id': canonical(input.path) },
    articleSection: input.section,
    keywords: input.keywords.join(', '),
    inLanguage: 'en',
    isAccessibleForFree: true,
    dateModified: input.dateModified,
    author: { '@type': 'Organization', name: SITE.name, url: `${SITE.baseUrl}/` },
    publisher: { '@type': 'Organization', name: SITE.name, url: `${SITE.baseUrl}/` },
  };
}

export function productSchema(input: {
  name: string;
  description: string;
  price: string;
  url: string;
}) {
  const numeric = Number(input.price.replace(/[^0-9.]/g, ''));
  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: input.name,
    description: input.description,
    brand: { '@type': 'Brand', name: SITE.name },
    offers: {
      '@type': 'Offer',
      url: input.url,
      price: numeric,
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
    },
  };
}
