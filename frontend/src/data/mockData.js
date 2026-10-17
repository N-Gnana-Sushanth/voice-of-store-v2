// Voice of Store — Single Source of Truth for Visual Replicas & Demo Data

export const DASHBOARD_KPIS = [
  {
    title: 'Total Feedback',
    value: '40,000',
    subtext: '↑ 12% vs last week',
    iconBg: '#eff6ff',
    iconColor: '#3b82f6',
    sparklineColor: '#3b82f6',
    sparklinePoints: 'M0,18 Q40,6 80,14 T160,8 T240,4',
  },
  {
    title: 'High Severity Issues',
    value: '326',
    subtext: '↑ 28% vs last week',
    iconBg: '#fee2e2',
    iconColor: '#ef4444',
    sparklineColor: '#ef4444',
    sparklinePoints: 'M0,16 Q40,18 80,10 T160,14 T240,2',
  },
  {
    title: 'Actionable Issues',
    value: '1,124',
    subtext: '↑ 18% vs last week',
    iconBg: '#e6f7ef',
    iconColor: '#10b981',
    sparklineColor: '#10b981',
    sparklinePoints: 'M0,20 Q40,12 80,16 T160,8 T240,6',
  },
  {
    title: 'Stores Covered',
    value: '436',
    subtext: 'Across 4 regions',
    iconBg: '#f3e8ff',
    iconColor: '#8b5cf6',
    sparklineColor: '#8b5cf6',
    sparklinePoints: 'M0,15 Q40,14 80,16 T160,12 T240,10',
  },
  {
    title: 'Avg. Response Time',
    value: '2.3 days',
    subtext: '↓ 35% vs last week',
    iconBg: '#fef3c7',
    iconColor: '#f59e0b',
    sparklineColor: '#f59e0b',
    sparklinePoints: 'M0,6 Q40,12 80,8 T160,16 T240,20',
  },
];

export const TOP_ISSUES = [
  {
    id: 1,
    title: 'Broken / Faulty Freezer',
    category: 'Equipment & Maintenance',
    severity: 'High',
    trend: 'up',
    affectedStores: '42 stores',
    owner: 'Store Ops',
    ownerTag: 'store-ops',
    evidence: 'Freezer not working again 😡 all frozen items spoiled...',
    icon: 'Snowflake',
  },
  {
    id: 2,
    title: 'Missing / Mislabeled Allergen Info',
    category: 'Food Safety & Compliance',
    severity: 'High',
    trend: 'up',
    affectedStores: '28 stores',
    owner: 'Quality & Compliance',
    ownerTag: 'quality',
    evidence: 'Allergen label missing on bakery items. Very risky...',
    icon: 'Utensils',
  },
  {
    id: 3,
    title: 'Rude / Unprofessional Staff Behaviour',
    category: 'Customer Service',
    severity: 'High',
    trend: 'up',
    affectedStores: '31 stores',
    owner: 'HR',
    ownerTag: 'hr',
    evidence: 'Staff at billing counter was very rude and shouted...',
    icon: 'Users',
  },
  {
    id: 4,
    title: 'Stock Out - Popular Items',
    category: 'Inventory & Supply',
    severity: 'Medium',
    trend: 'down',
    affectedStores: '56 stores',
    owner: 'Supply Chain',
    ownerTag: 'supply',
    evidence: 'Rice and oil out of stock again. Need immediate refill.',
    icon: 'Package',
  },
  {
    id: 5,
    title: 'App / Payment Issues',
    category: 'Digital Experience',
    severity: 'Medium',
    trend: 'down',
    affectedStores: '38 stores',
    owner: 'Digital',
    ownerTag: 'digital',
    evidence: 'App payment failed 3 times. Had to leave without buying.',
    icon: 'Smartphone',
  },
];

export const FEEDBACK_SOURCES = [
  { name: 'Online Reviews', percentage: 38, count: 15200, color: '#3b82f6' },
  { name: 'In-App Comments', percentage: 26, count: 10400, color: '#10b981' },
  { name: 'Store Staff Notes', percentage: 21, count: 8400, color: '#f97316' },
  { name: 'Call Centre Tickets', percentage: 15, count: 6000, color: '#8b5cf6' },
];

export const SENTIMENT_TREND = [
  { date: '12 Oct', Positive: 4800, Neutral: 3100, Negative: 1200 },
  { date: '13 Oct', Positive: 4600, Neutral: 3250, Negative: 1350 },
  { date: '14 Oct', Positive: 5050, Neutral: 2900, Negative: 1100 },
  { date: '15 Oct', Positive: 4700, Neutral: 3300, Negative: 1500 },
  { date: '16 Oct', Positive: 4900, Neutral: 3200, Negative: 1400 },
  { date: '17 Oct', Positive: 5200, Neutral: 3000, Negative: 1250 },
  { date: '18 Oct', Positive: 5100, Neutral: 3400, Negative: 1600 },
];

export const EMERGING_ISSUES_DASHBOARD = [
  {
    issue: 'Refrigeration not working',
    store: 'Store #128',
    volume: 12,
    change: '↑ 300%',
    severity: 'High',
  },
  {
    issue: 'Insect found in bakery item',
    store: 'Store #074',
    volume: 8,
    change: '↑ 250%',
    severity: 'High',
  },
  {
    issue: 'Staff rude at billing',
    store: 'Store #302',
    volume: 10,
    change: '↑ 200%',
    severity: 'High',
  },
];

export const RECENT_FEEDBACK_SAMPLES = [
  {
    channel: 'Google',
    time: '2 hours ago',
    text: 'Freezer not working again 😡 food items spoiled... pls fix asap #Chennai',
  },
  {
    channel: 'AppStore',
    time: '1 day ago',
    text: 'Milk section me bahut smell hai :(',
  },
  {
    channel: 'WhatsApp',
    time: '3 hours ago',
    text: 'Stock khatam ho gaya aaj bhi...',
  },
];

export const REGIONAL_HIGHLIGHTS = [
  { region: 'South', change: '↑ 18% issues', isUp: true },
  { region: 'West', change: '↑ 12% issues', isUp: true },
  { region: 'North', change: '↓ 8% issues', isUp: false },
  { region: 'East', change: '↑ 5% issues', isUp: true },
];

export const FEEDBACK_STREAM_DATA = [
  {
    id: 'fb-1',
    channel: 'Online Review',
    channelType: 'google',
    time: '16 Oct 2026, 10:24 AM',
    text: 'Freezer not working again 😡 food items spoiled. Staff not responding even after complaint.',
    meta: 'Store #128 • Chennai • English',
    tags: [
      { label: 'Equipment Issue', color: 'blue' },
      { label: 'Perishable Loss', color: 'purple' },
    ],
    sentiment: 'Negative',
    severity: 'High',
  },
  {
    id: 'fb-2',
    channel: 'In-App Comment',
    channelType: 'appstore',
    time: '16 Oct 2026, 09:18 AM',
    text: 'Milk section me bahut smell hai. Lagta hai milk packets expired hai. Please check 🙏',
    meta: 'Store #074 • Pune • Hinglish',
    tags: [
      { label: 'Hygiene', color: 'yellow' },
      { label: 'Expired Products', color: 'pink' },
    ],
    sentiment: 'Negative',
    severity: 'High',
  },
  {
    id: 'fb-3',
    channel: 'Store Staff Note',
    channelType: 'staff',
    time: '16 Oct 2026, 08:45 AM',
    text: 'AC not working in back storage area. Temperature high. Need maintenance ASAP.',
    meta: 'Store #302 • Bengaluru • English',
    tags: [
      { label: 'Equipment Issue', color: 'blue' },
      { label: 'Maintenance', color: 'purple' },
    ],
    sentiment: 'Neutral',
    severity: 'Medium',
  },
  {
    id: 'fb-4',
    channel: 'Call Centre Ticket',
    channelType: 'call',
    time: '16 Oct 2026, 08:12 AM',
    text: 'Customer complained about rude behaviour at billing counter. Says staff was shouting.',
    meta: 'Store #215 • Hyderabad • English',
    tags: [
      { label: 'Staff Behaviour', color: 'orange' },
      { label: 'Customer Service', color: 'purple' },
    ],
    sentiment: 'Negative',
    severity: 'High',
  },
  {
    id: 'fb-5',
    channel: 'Online Review',
    channelType: 'google',
    time: '15 Oct 2026, 07:56 PM',
    text: 'Nice store and good variety. Staff was helpful 👍',
    meta: 'Store #091 • Visakhapatnam • English',
    tags: [
      { label: 'Positive Feedback', color: 'green' },
    ],
    sentiment: 'Positive',
    severity: 'Low',
  },
  {
    id: 'fb-6',
    channel: 'In-App Comment',
    channelType: 'appstore',
    time: '15 Oct 2026, 06:30 PM',
    text: 'Allergen label missing on bakery item. Very dangerous for people with allergies.',
    meta: 'Store #074 • Pune • English',
    tags: [
      { label: 'Allergen Mislabel', color: 'yellow' },
      { label: 'Food Safety', color: 'purple' },
    ],
    sentiment: 'Negative',
    severity: 'High',
  },
  {
    id: 'fb-7',
    channel: 'Store Staff Note',
    channelType: 'staff',
    time: '15 Oct 2026, 05:12 PM',
    text: 'Stock of popular items (rice, oil) running low. Need replenishment.',
    meta: 'Store #412 • Coimbatore • English',
    tags: [
      { label: 'Stock Out', color: 'blue' },
      { label: 'Inventory', color: 'purple' },
    ],
    sentiment: 'Neutral',
    severity: 'Medium',
  },
  {
    id: 'fb-8',
    channel: 'Call Centre Ticket',
    channelType: 'call',
    time: '15 Oct 2026, 04:48 PM',
    text: 'App payment failed multiple times. Customer had to leave without purchase.',
    meta: 'Store #128 • Chennai • English',
    tags: [
      { label: 'Payment Issue', color: 'pink' },
      { label: 'Digital', color: 'purple' },
    ],
    sentiment: 'Negative',
    severity: 'Medium',
  },
];

export const ISSUE_ANALYSIS_CATEGORIES = [
  { name: 'Equipment & Maintenance', count: 420, color: '#3b82f6', icon: 'Snowflake' },
  { name: 'Food Safety & Compliance', count: 320, color: '#f97316', icon: 'Utensils' },
  { name: 'Customer Service', count: 280, color: '#8b5cf6', icon: 'Users' },
  { name: 'Inventory & Stock', count: 210, color: '#10b981', icon: 'Package' },
  { name: 'Payments & Digital', count: 160, color: '#ef4444', icon: 'Smartphone' },
  { name: 'Store Cleanliness', count: 120, color: '#eab308', icon: 'Sparkles' },
  { name: 'Pricing & Merchandising', count: 90, color: '#c084fc', icon: 'Tag' },
  { name: 'Staff Behaviour', count: 80, color: '#60a5fa', icon: 'UserCheck' },
  { name: 'Others', count: 60, color: '#93c5fd', icon: 'MoreHorizontal' },
];

export const ISSUE_TREND_WEEKLY = [
  { date: '12 Oct', Equipment: 340, FoodSafety: 240, CustomerService: 190, Inventory: 120, Payments: 80 },
  { date: '13 Oct', Equipment: 380, FoodSafety: 280, CustomerService: 230, Inventory: 140, Payments: 95 },
  { date: '14 Oct', Equipment: 360, FoodSafety: 270, CustomerService: 220, Inventory: 160, Payments: 110 },
  { date: '15 Oct', Equipment: 440, FoodSafety: 340, CustomerService: 260, Inventory: 190, Payments: 130 },
  { date: '16 Oct', Equipment: 410, FoodSafety: 310, CustomerService: 270, Inventory: 180, Payments: 145 },
  { date: '17 Oct', Equipment: 430, FoodSafety: 320, CustomerService: 290, Inventory: 200, Payments: 150 },
  { date: '18 Oct', Equipment: 470, FoodSafety: 350, CustomerService: 280, Inventory: 210, Payments: 160 },
];

export const SEVERITY_DISTRIBUTION = [
  { name: 'High', count: 326, percentage: 29, color: '#ef4444' },
  { name: 'Medium', count: 498, percentage: 44, color: '#f97316' },
  { name: 'Low', count: 300, percentage: 27, color: '#10b981' },
];

export const EMERGING_DETAILED_CARDS = [
  {
    id: 'em-1',
    title: 'Refrigeration not working',
    tagCategory: 'Equipment & Maintenance',
    tagOwner: 'Store Ops',
    tagOwnerType: 'store-ops',
    narrative: 'Mentions increased from 2 to 18 this week (+800%). Mostly reported from a single store.',
    currentMentions: 18,
    previousWeek: 2,
    increasePct: '+800%',
    store: '#128 (Chennai)',
    severity: 'High',
    icon: 'Snowflake',
    iconBg: '#fee2e2',
    iconColor: '#ef4444',
  },
  {
    id: 'em-2',
    title: 'Allergen label missing on bakery items',
    tagCategory: 'Food Safety & Compliance',
    tagOwner: 'Quality & Compliance',
    tagOwnerType: 'quality',
    narrative: 'Mentions increased from 3 to 14 this week (+367%). Reported by multiple channels (reviews + staff notes).',
    currentMentions: 14,
    previousWeek: 3,
    increasePct: '+367%',
    store: '#074 (Pune)',
    severity: 'High',
    icon: 'Utensils',
    iconBg: '#fef3c7',
    iconColor: '#f59e0b',
  },
  {
    id: 'em-3',
    title: 'Rude staff behaviour at billing',
    tagCategory: 'Customer Service',
    tagOwner: 'HR',
    tagOwnerType: 'hr',
    narrative: 'Mentions increased from 1 to 9 this week (+800%). Reported in app comments and call centre tickets.',
    currentMentions: 9,
    previousWeek: 1,
    increasePct: '+800%',
    store: '#302 (Bengaluru)',
    severity: 'Medium',
    icon: 'Users',
    iconBg: '#f3e8ff',
    iconColor: '#8b5cf6',
  },
];

export const EMERGING_TREND_COMPARISON = [
  { date: '12 Oct', currentIssue: 2, sameIssueOther: 2, overallAvg: 1 },
  { date: '13 Oct', currentIssue: 4, sameIssueOther: 2.5, overallAvg: 1.2 },
  { date: '14 Oct', currentIssue: 6, sameIssueOther: 3, overallAvg: 1.5 },
  { date: '15 Oct', currentIssue: 9, sameIssueOther: 3.5, overallAvg: 1.8 },
  { date: '16 Oct', currentIssue: 12, sameIssueOther: 4, overallAvg: 2 },
  { date: '17 Oct', currentIssue: 15, sameIssueOther: 4.5, overallAvg: 2.2 },
  { date: '18 Oct', currentIssue: 18, sameIssueOther: 5, overallAvg: 2.5 },
];

export const EMERGING_CHANNEL_BREAKDOWN = [
  { name: 'Online Reviews', percentage: 44, count: 8, color: '#ef4444' },
  { name: 'In-App Comments', percentage: 28, count: 5, color: '#3b82f6' },
  { name: 'Store Staff Notes', percentage: 17, count: 3, color: '#10b981' },
  { name: 'Call Centre Tickets', percentage: 11, count: 2, color: '#8b5cf6' },
];

export const PLANTED_EVALUATIONS = [
  {
    incident: 'Incident 1: Freezer Failure',
    firstDetected: 'Day -10',
    actualPeak: 'Day 0',
    leadTime: '10 days',
    status: 'Detected Early',
  },
  {
    incident: 'Incident 2: Allergen Mislabel',
    firstDetected: 'Day -8',
    actualPeak: 'Day 0',
    leadTime: '8 days',
    status: 'Detected Early',
  },
  {
    incident: 'Incident 3: Staff Misconduct',
    firstDetected: 'Day -12',
    actualPeak: 'Day 0',
    leadTime: '12 days',
    status: 'Detected Early',
  },
];
