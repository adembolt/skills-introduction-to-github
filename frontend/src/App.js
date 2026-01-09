import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { 
  LayoutDashboard, Users, Package, FileText, ShoppingCart, 
  Settings, Activity, Menu, X, Plus, Search, Edit, Trash2,
  ChevronDown, ChevronRight, TrendingUp, DollarSign, Eye,
  Clock, CheckCircle, XCircle, AlertCircle, RefreshCw,
  Home, LogOut, Bell, User, BarChart3, Layers, FolderOpen
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import { Toaster, toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// API Helper
const api = {
  get: async (url) => {
    const response = await axios.get(`${API}${url}`);
    return response.data;
  },
  post: async (url, data) => {
    const response = await axios.post(`${API}${url}`, data);
    return response.data;
  },
  put: async (url, data) => {
    const response = await axios.put(`${API}${url}`, data);
    return response.data;
  },
  delete: async (url) => {
    const response = await axios.delete(`${API}${url}`);
    return response.data;
  }
};

// Sidebar Navigation Items
const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "users", label: "Kullanıcılar", icon: Users },
  { id: "products", label: "Ürünler", icon: Package },
  { id: "pages", label: "Sayfalar", icon: FileText },
  { id: "orders", label: "Siparişler", icon: ShoppingCart },
  { id: "categories", label: "Kategoriler", icon: FolderOpen },
  { id: "activity", label: "Aktivite Logları", icon: Activity },
  { id: "settings", label: "Ayarlar", icon: Settings },
];

// Status Colors
const statusColors = {
  active: "bg-green-100 text-green-800",
  inactive: "bg-gray-100 text-gray-800",
  banned: "bg-red-100 text-red-800",
  pending: "bg-yellow-100 text-yellow-800",
  processing: "bg-blue-100 text-blue-800",
  shipped: "bg-purple-100 text-purple-800",
  delivered: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
  draft: "bg-gray-100 text-gray-800",
  published: "bg-green-100 text-green-800",
  archived: "bg-orange-100 text-orange-800",
};

const roleColors = {
  admin: "bg-red-100 text-red-800",
  editor: "bg-blue-100 text-blue-800",
  user: "bg-gray-100 text-gray-800",
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

// ============ COMPONENTS ============

// Sidebar Component
const Sidebar = ({ activeTab, setActiveTab, isOpen, setIsOpen }) => {
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-slate-900 text-white
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-4 border-b border-slate-700">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <Layers className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg">Admin Panel</span>
            </div>
            <button 
              className="lg:hidden text-slate-400 hover:text-white"
              onClick={() => setIsOpen(false)}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                data-testid={`nav-${item.id}`}
                onClick={() => {
                  setActiveTab(item.id);
                  setIsOpen(false);
                }}
                className={`
                  w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                  transition-colors duration-200
                  ${activeTab === item.id 
                    ? 'bg-blue-600 text-white' 
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'}
                `}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
          
          {/* Footer */}
          <div className="p-4 border-t border-slate-700">
            <div className="flex items-center gap-3 px-3 py-2">
              <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                <User className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Admin</p>
                <p className="text-xs text-slate-400">admin@site.com</p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

// Header Component
const Header = ({ setIsOpen }) => {
  return (
    <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between sticky top-0 z-30">
      <button 
        className="lg:hidden p-2 hover:bg-slate-100 rounded-lg"
        onClick={() => setIsOpen(true)}
        data-testid="mobile-menu-btn"
      >
        <Menu className="w-5 h-5" />
      </button>
      
      <div className="flex-1 max-w-md mx-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input 
            placeholder="Ara..." 
            className="pl-9 bg-slate-50 border-slate-200"
            data-testid="global-search"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="relative" data-testid="notifications-btn">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </Button>
        <Button variant="ghost" size="icon" data-testid="profile-btn">
          <User className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
};

// Stats Card Component
const StatsCard = ({ title, value, icon: Icon, trend, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600",
    orange: "bg-orange-50 text-orange-600",
  };
  
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500 mb-1">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {trend && (
              <p className={`text-xs mt-1 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {trend > 0 ? '+' : ''}{trend}% geçen aya göre
              </p>
            )}
          </div>
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============ DASHBOARD PAGE ============
const DashboardPage = ({ stats, loading, onRefresh }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-slate-500">Hoş geldiniz! İşte sitenizin genel durumu.</p>
        </div>
        <Button onClick={onRefresh} variant="outline" data-testid="refresh-stats">
          <RefreshCw className="w-4 h-4 mr-2" />
          Yenile
        </Button>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard 
          title="Toplam Kullanıcı" 
          value={stats.total_users || 0}
          icon={Users}
          trend={12}
          color="blue"
        />
        <StatsCard 
          title="Toplam Ürün" 
          value={stats.total_products || 0}
          icon={Package}
          trend={8}
          color="green"
        />
        <StatsCard 
          title="Toplam Sipariş" 
          value={stats.total_orders || 0}
          icon={ShoppingCart}
          trend={-3}
          color="purple"
        />
        <StatsCard 
          title="Toplam Gelir" 
          value={`₺${(stats.total_revenue || 0).toLocaleString('tr-TR')}`}
          icon={DollarSign}
          trend={15}
          color="orange"
        />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Aylık Gelir</CardTitle>
            <CardDescription>Son 6 ayın gelir grafiği</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.monthly_revenue || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `₺${value.toLocaleString('tr-TR')}`} />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Sipariş Durumları</CardTitle>
            <CardDescription>Siparişlerin dağılımı</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.order_statuses || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {(stats.order_statuses || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Aktif Kullanıcılar</p>
                <p className="text-xl font-bold">{stats.active_users || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Eye className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Yayında Ürün</p>
                <p className="text-xl font-bold">{stats.published_products || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Bekleyen Siparişler</p>
                <p className="text-xl font-bold">{stats.pending_orders || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// ============ USERS PAGE ============
const UsersPage = ({ users, loading, onRefresh, onCreate, onUpdate, onDelete }) => {
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    name: "", email: "", phone: "", role: "user", status: "active", password: ""
  });

  const filteredUsers = users.filter(user => 
    user.name?.toLowerCase().includes(search.toLowerCase()) ||
    user.email?.toLowerCase().includes(search.toLowerCase())
  );

  const openModal = (user = null) => {
    if (user) {
      setEditingUser(user);
      setFormData({ ...user, password: "" });
    } else {
      setEditingUser(null);
      setFormData({ name: "", email: "", phone: "", role: "user", status: "active", password: "" });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingUser) {
        await onUpdate(editingUser.id, formData);
        toast.success("Kullanıcı başarıyla güncellendi");
      } else {
        await onCreate(formData);
        toast.success("Kullanıcı başarıyla oluşturuldu");
      }
      setIsModalOpen(false);
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu kullanıcıyı silmek istediğinize emin misiniz?")) {
      try {
        await onDelete(id);
        toast.success("Kullanıcı başarıyla silindi");
        onRefresh();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Kullanıcılar</h1>
          <p className="text-slate-500">Tüm kullanıcıları yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-user-btn">
          <Plus className="w-4 h-4 mr-2" />
          Yeni Kullanıcı
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input 
                placeholder="Kullanıcı ara..." 
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                data-testid="search-users"
              />
            </div>
            <Button variant="outline" onClick={onRefresh}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kullanıcı</TableHead>
                  <TableHead>E-posta</TableHead>
                  <TableHead>Telefon</TableHead>
                  <TableHead>Rol</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id} data-testid={`user-row-${user.id}`}>
                    <TableCell className="font-medium">{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.phone || "-"}</TableCell>
                    <TableCell>
                      <Badge className={roleColors[user.role]}>{user.role}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColors[user.status]}>{user.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openModal(user)} data-testid={`edit-user-${user.id}`}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(user.id)} data-testid={`delete-user-${user.id}`}>
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {filteredUsers.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-slate-500">
                      Kullanıcı bulunamadı
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* User Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingUser ? "Kullanıcı Düzenle" : "Yeni Kullanıcı"}</DialogTitle>
            <DialogDescription>
              {editingUser ? "Kullanıcı bilgilerini güncelleyin" : "Yeni bir kullanıcı oluşturun"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Ad Soyad</Label>
              <Input 
                id="name" 
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                data-testid="user-name-input"
              />
            </div>
            <div>
              <Label htmlFor="email">E-posta</Label>
              <Input 
                id="email" 
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                data-testid="user-email-input"
              />
            </div>
            <div>
              <Label htmlFor="phone">Telefon</Label>
              <Input 
                id="phone" 
                value={formData.phone || ""}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                data-testid="user-phone-input"
              />
            </div>
            {!editingUser && (
              <div>
                <Label htmlFor="password">Şifre</Label>
                <Input 
                  id="password" 
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  data-testid="user-password-input"
                />
              </div>
            )}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="role">Rol</Label>
                <Select value={formData.role} onValueChange={(v) => setFormData({...formData, role: v})}>
                  <SelectTrigger data-testid="user-role-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="editor">Editör</SelectItem>
                    <SelectItem value="user">Kullanıcı</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="status">Durum</Label>
                <Select value={formData.status} onValueChange={(v) => setFormData({...formData, status: v})}>
                  <SelectTrigger data-testid="user-status-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Aktif</SelectItem>
                    <SelectItem value="inactive">Pasif</SelectItem>
                    <SelectItem value="banned">Yasaklı</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit} data-testid="save-user-btn">Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ PRODUCTS PAGE ============
const ProductsPage = ({ products, categories, loading, onRefresh, onCreate, onUpdate, onDelete }) => {
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: "", description: "", price: 0, category: "", stock: 0, status: "draft", image: ""
  });

  const filteredProducts = products.filter(product => 
    product.name?.toLowerCase().includes(search.toLowerCase()) ||
    product.description?.toLowerCase().includes(search.toLowerCase())
  );

  const openModal = (product = null) => {
    if (product) {
      setEditingProduct(product);
      setFormData({ ...product });
    } else {
      setEditingProduct(null);
      setFormData({ name: "", description: "", price: 0, category: "", stock: 0, status: "draft", image: "" });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingProduct) {
        await onUpdate(editingProduct.id, formData);
        toast.success("Ürün başarıyla güncellendi");
      } else {
        await onCreate(formData);
        toast.success("Ürün başarıyla oluşturuldu");
      }
      setIsModalOpen(false);
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu ürünü silmek istediğinize emin misiniz?")) {
      try {
        await onDelete(id);
        toast.success("Ürün başarıyla silindi");
        onRefresh();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ürünler</h1>
          <p className="text-slate-500">Tüm ürünleri yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-product-btn">
          <Plus className="w-4 h-4 mr-2" />
          Yeni Ürün
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input 
                placeholder="Ürün ara..." 
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                data-testid="search-products"
              />
            </div>
            <Button variant="outline" onClick={onRefresh}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Ürün</TableHead>
                  <TableHead>Kategori</TableHead>
                  <TableHead>Fiyat</TableHead>
                  <TableHead>Stok</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.map((product) => (
                  <TableRow key={product.id} data-testid={`product-row-${product.id}`}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{product.name}</p>
                        <p className="text-sm text-slate-500 truncate max-w-xs">{product.description}</p>
                      </div>
                    </TableCell>
                    <TableCell>{product.category || "-"}</TableCell>
                    <TableCell>₺{product.price?.toLocaleString('tr-TR')}</TableCell>
                    <TableCell>{product.stock}</TableCell>
                    <TableCell>
                      <Badge className={statusColors[product.status]}>{product.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openModal(product)} data-testid={`edit-product-${product.id}`}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(product.id)} data-testid={`delete-product-${product.id}`}>
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {filteredProducts.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-slate-500">
                      Ürün bulunamadı
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Product Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingProduct ? "Ürün Düzenle" : "Yeni Ürün"}</DialogTitle>
            <DialogDescription>
              {editingProduct ? "Ürün bilgilerini güncelleyin" : "Yeni bir ürün oluşturun"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="product-name">Ürün Adı</Label>
              <Input 
                id="product-name" 
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                data-testid="product-name-input"
              />
            </div>
            <div>
              <Label htmlFor="product-desc">Açıklama</Label>
              <Textarea 
                id="product-desc" 
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                data-testid="product-desc-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="product-price">Fiyat (₺)</Label>
                <Input 
                  id="product-price" 
                  type="number"
                  value={formData.price}
                  onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value) || 0})}
                  data-testid="product-price-input"
                />
              </div>
              <div>
                <Label htmlFor="product-stock">Stok</Label>
                <Input 
                  id="product-stock" 
                  type="number"
                  value={formData.stock}
                  onChange={(e) => setFormData({...formData, stock: parseInt(e.target.value) || 0})}
                  data-testid="product-stock-input"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="product-category">Kategori</Label>
                <Select value={formData.category} onValueChange={(v) => setFormData({...formData, category: v})}>
                  <SelectTrigger data-testid="product-category-select">
                    <SelectValue placeholder="Seçin" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => (
                      <SelectItem key={cat.id} value={cat.name}>{cat.name}</SelectItem>
                    ))}
                    <SelectItem value="Diğer">Diğer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="product-status">Durum</Label>
                <Select value={formData.status} onValueChange={(v) => setFormData({...formData, status: v})}>
                  <SelectTrigger data-testid="product-status-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Taslak</SelectItem>
                    <SelectItem value="published">Yayında</SelectItem>
                    <SelectItem value="archived">Arşiv</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="product-image">Görsel URL</Label>
              <Input 
                id="product-image" 
                value={formData.image || ""}
                onChange={(e) => setFormData({...formData, image: e.target.value})}
                placeholder="https://..."
                data-testid="product-image-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit} data-testid="save-product-btn">Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ PAGES PAGE ============
const PagesPage = ({ pages, loading, onRefresh, onCreate, onUpdate, onDelete }) => {
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPage, setEditingPage] = useState(null);
  const [formData, setFormData] = useState({
    title: "", slug: "", content: "", meta_title: "", meta_description: "", status: "draft"
  });

  const filteredPages = pages.filter(page => 
    page.title?.toLowerCase().includes(search.toLowerCase()) ||
    page.slug?.toLowerCase().includes(search.toLowerCase())
  );

  const openModal = (page = null) => {
    if (page) {
      setEditingPage(page);
      setFormData({ ...page });
    } else {
      setEditingPage(null);
      setFormData({ title: "", slug: "", content: "", meta_title: "", meta_description: "", status: "draft" });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingPage) {
        await onUpdate(editingPage.id, formData);
        toast.success("Sayfa başarıyla güncellendi");
      } else {
        await onCreate(formData);
        toast.success("Sayfa başarıyla oluşturuldu");
      }
      setIsModalOpen(false);
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu sayfayı silmek istediğinize emin misiniz?")) {
      try {
        await onDelete(id);
        toast.success("Sayfa başarıyla silindi");
        onRefresh();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Sayfalar</h1>
          <p className="text-slate-500">Site sayfalarını yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-page-btn">
          <Plus className="w-4 h-4 mr-2" />
          Yeni Sayfa
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input 
                placeholder="Sayfa ara..." 
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                data-testid="search-pages"
              />
            </div>
            <Button variant="outline" onClick={onRefresh}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Başlık</TableHead>
                  <TableHead>Slug</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Güncelleme</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPages.map((page) => (
                  <TableRow key={page.id} data-testid={`page-row-${page.id}`}>
                    <TableCell className="font-medium">{page.title}</TableCell>
                    <TableCell>/{page.slug}</TableCell>
                    <TableCell>
                      <Badge className={statusColors[page.status]}>{page.status}</Badge>
                    </TableCell>
                    <TableCell>
                      {page.updated_at ? new Date(page.updated_at).toLocaleDateString('tr-TR') : "-"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openModal(page)} data-testid={`edit-page-${page.id}`}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(page.id)} data-testid={`delete-page-${page.id}`}>
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {filteredPages.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-slate-500">
                      Sayfa bulunamadı
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Page Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingPage ? "Sayfa Düzenle" : "Yeni Sayfa"}</DialogTitle>
            <DialogDescription>
              {editingPage ? "Sayfa bilgilerini güncelleyin" : "Yeni bir sayfa oluşturun"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="page-title">Başlık</Label>
                <Input 
                  id="page-title" 
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  data-testid="page-title-input"
                />
              </div>
              <div>
                <Label htmlFor="page-slug">Slug</Label>
                <Input 
                  id="page-slug" 
                  value={formData.slug}
                  onChange={(e) => setFormData({...formData, slug: e.target.value.toLowerCase().replace(/\s+/g, '-')})}
                  data-testid="page-slug-input"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="page-content">İçerik</Label>
              <Textarea 
                id="page-content" 
                rows={6}
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                data-testid="page-content-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="page-meta-title">Meta Başlık (SEO)</Label>
                <Input 
                  id="page-meta-title" 
                  value={formData.meta_title || ""}
                  onChange={(e) => setFormData({...formData, meta_title: e.target.value})}
                  data-testid="page-meta-title-input"
                />
              </div>
              <div>
                <Label htmlFor="page-status">Durum</Label>
                <Select value={formData.status} onValueChange={(v) => setFormData({...formData, status: v})}>
                  <SelectTrigger data-testid="page-status-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Taslak</SelectItem>
                    <SelectItem value="published">Yayında</SelectItem>
                    <SelectItem value="archived">Arşiv</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="page-meta-desc">Meta Açıklama (SEO)</Label>
              <Textarea 
                id="page-meta-desc" 
                rows={2}
                value={formData.meta_description || ""}
                onChange={(e) => setFormData({...formData, meta_description: e.target.value})}
                data-testid="page-meta-desc-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit} data-testid="save-page-btn">Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ ORDERS PAGE ============
const OrdersPage = ({ orders, loading, onRefresh, onUpdate, onDelete }) => {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedOrder, setSelectedOrder] = useState(null);

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.customer_name?.toLowerCase().includes(search.toLowerCase()) ||
      order.customer_email?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "all" || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await onUpdate(orderId, { status: newStatus });
      toast.success("Sipariş durumu güncellendi");
      onRefresh();
    } catch (error) {
      toast.error("Güncelleme başarısız");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu siparişi silmek istediğinize emin misiniz?")) {
      try {
        await onDelete(id);
        toast.success("Sipariş başarıyla silindi");
        onRefresh();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Siparişler</h1>
          <p className="text-slate-500">Tüm siparişleri yönetin</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input 
                placeholder="Sipariş ara..." 
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                data-testid="search-orders"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40" data-testid="order-status-filter">
                <SelectValue placeholder="Durum" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tümü</SelectItem>
                <SelectItem value="pending">Beklemede</SelectItem>
                <SelectItem value="processing">İşleniyor</SelectItem>
                <SelectItem value="shipped">Kargoda</SelectItem>
                <SelectItem value="delivered">Teslim Edildi</SelectItem>
                <SelectItem value="cancelled">İptal</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={onRefresh}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Sipariş No</TableHead>
                  <TableHead>Müşteri</TableHead>
                  <TableHead>Toplam</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Tarih</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOrders.map((order) => (
                  <TableRow key={order.id} data-testid={`order-row-${order.id}`}>
                    <TableCell className="font-mono">#{order.id?.slice(0, 8)}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{order.customer_name}</p>
                        <p className="text-sm text-slate-500">{order.customer_email}</p>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">₺{order.total?.toLocaleString('tr-TR')}</TableCell>
                    <TableCell>
                      <Select 
                        value={order.status} 
                        onValueChange={(v) => handleStatusChange(order.id, v)}
                      >
                        <SelectTrigger className="w-32" data-testid={`order-status-${order.id}`}>
                          <Badge className={statusColors[order.status]}>{order.status}</Badge>
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pending">Beklemede</SelectItem>
                          <SelectItem value="processing">İşleniyor</SelectItem>
                          <SelectItem value="shipped">Kargoda</SelectItem>
                          <SelectItem value="delivered">Teslim Edildi</SelectItem>
                          <SelectItem value="cancelled">İptal</SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      {order.created_at ? new Date(order.created_at).toLocaleDateString('tr-TR') : "-"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => setSelectedOrder(order)} data-testid={`view-order-${order.id}`}>
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(order.id)} data-testid={`delete-order-${order.id}`}>
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {filteredOrders.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-slate-500">
                      Sipariş bulunamadı
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Order Detail Modal */}
      <Dialog open={!!selectedOrder} onOpenChange={() => setSelectedOrder(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Sipariş Detayı</DialogTitle>
            <DialogDescription>
              #{selectedOrder?.id?.slice(0, 8)}
            </DialogDescription>
          </DialogHeader>
          {selectedOrder && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-500">Müşteri</Label>
                  <p className="font-medium">{selectedOrder.customer_name}</p>
                </div>
                <div>
                  <Label className="text-slate-500">E-posta</Label>
                  <p>{selectedOrder.customer_email}</p>
                </div>
                <div>
                  <Label className="text-slate-500">Telefon</Label>
                  <p>{selectedOrder.customer_phone || "-"}</p>
                </div>
                <div>
                  <Label className="text-slate-500">Durum</Label>
                  <Badge className={statusColors[selectedOrder.status]}>{selectedOrder.status}</Badge>
                </div>
              </div>
              <div>
                <Label className="text-slate-500">Adres</Label>
                <p>{selectedOrder.shipping_address}</p>
              </div>
              <Separator />
              <div>
                <Label className="text-slate-500 mb-2 block">Ürünler</Label>
                {selectedOrder.items?.map((item, idx) => (
                  <div key={idx} className="flex justify-between py-2 border-b last:border-0">
                    <span>{item.product_name} x{item.quantity}</span>
                    <span className="font-medium">₺{(item.price * item.quantity).toLocaleString('tr-TR')}</span>
                  </div>
                ))}
                <div className="flex justify-between py-2 font-bold">
                  <span>Toplam</span>
                  <span>₺{selectedOrder.total?.toLocaleString('tr-TR')}</span>
                </div>
              </div>
              {selectedOrder.notes && (
                <div>
                  <Label className="text-slate-500">Notlar</Label>
                  <p>{selectedOrder.notes}</p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedOrder(null)}>Kapat</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ CATEGORIES PAGE ============
const CategoriesPage = ({ categories, loading, onRefresh, onCreate, onDelete }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: "", description: "" });

  const handleSubmit = async () => {
    try {
      await onCreate(formData);
      toast.success("Kategori başarıyla oluşturuldu");
      setIsModalOpen(false);
      setFormData({ name: "", description: "" });
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu kategoriyi silmek istediğinize emin misiniz?")) {
      try {
        await onDelete(id);
        toast.success("Kategori başarıyla silindi");
        onRefresh();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Kategoriler</h1>
          <p className="text-slate-500">Ürün kategorilerini yönetin</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} data-testid="add-category-btn">
          <Plus className="w-4 h-4 mr-2" />
          Yeni Kategori
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full flex items-center justify-center h-32">
            <RefreshCw className="w-6 h-6 animate-spin" />
          </div>
        ) : (
          categories.map((category) => (
            <Card key={category.id} data-testid={`category-card-${category.id}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{category.name}</h3>
                    <p className="text-sm text-slate-500 mt-1">{category.description || "Açıklama yok"}</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(category.id)} data-testid={`delete-category-${category.id}`}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
        {!loading && categories.length === 0 && (
          <div className="col-span-full text-center py-8 text-slate-500">
            Kategori bulunamadı
          </div>
        )}
      </div>

      {/* Category Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Yeni Kategori</DialogTitle>
            <DialogDescription>
              Yeni bir ürün kategorisi oluşturun
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="category-name">Kategori Adı</Label>
              <Input 
                id="category-name" 
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                data-testid="category-name-input"
              />
            </div>
            <div>
              <Label htmlFor="category-desc">Açıklama</Label>
              <Textarea 
                id="category-desc" 
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                data-testid="category-desc-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit} data-testid="save-category-btn">Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ ACTIVITY LOGS PAGE ============
const ActivityLogsPage = ({ logs, loading, onRefresh }) => {
  const getActionIcon = (action) => {
    switch (action) {
      case "CREATE": return <Plus className="w-4 h-4 text-green-500" />;
      case "UPDATE": return <Edit className="w-4 h-4 text-blue-500" />;
      case "DELETE": return <Trash2 className="w-4 h-4 text-red-500" />;
      default: return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case "CREATE": return "bg-green-100 text-green-800";
      case "UPDATE": return "bg-blue-100 text-blue-800";
      case "DELETE": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Aktivite Logları</h1>
          <p className="text-slate-500">Sistemdeki tüm aktiviteleri takip edin</p>
        </div>
        <Button variant="outline" onClick={onRefresh} data-testid="refresh-logs">
          <RefreshCw className="w-4 h-4 mr-2" />
          Yenile
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : (
            <ScrollArea className="h-[600px]">
              <div className="divide-y">
                {logs.map((log) => (
                  <div key={log.id} className="p-4 hover:bg-slate-50 flex items-start gap-4" data-testid={`log-${log.id}`}>
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                      {getActionIcon(log.action)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <Badge className={getActionColor(log.action)}>{log.action}</Badge>
                        <Badge variant="outline">{log.entity_type}</Badge>
                      </div>
                      <p className="text-sm mt-1">{log.details}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                        <span>{log.user_name || "Sistem"}</span>
                        <span>•</span>
                        <span>{log.created_at ? new Date(log.created_at).toLocaleString('tr-TR') : "-"}</span>
                      </div>
                    </div>
                  </div>
                ))}
                {logs.length === 0 && (
                  <div className="text-center py-8 text-slate-500">
                    Aktivite bulunamadı
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ============ SETTINGS PAGE ============
const SettingsPage = ({ settings, loading, onUpdate }) => {
  const [formData, setFormData] = useState(settings || {});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setFormData(settings || {});
  }, [settings]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onUpdate(formData);
      toast.success("Ayarlar başarıyla kaydedildi");
    } catch (error) {
      toast.error("Kaydetme işlemi başarısız");
    }
    setSaving(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ayarlar</h1>
          <p className="text-slate-500">Site ayarlarını yönetin</p>
        </div>
        <Button onClick={handleSave} disabled={saving} data-testid="save-settings-btn">
          {saving ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
          Kaydet
        </Button>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general" data-testid="tab-general">Genel</TabsTrigger>
          <TabsTrigger value="contact" data-testid="tab-contact">İletişim</TabsTrigger>
          <TabsTrigger value="social" data-testid="tab-social">Sosyal Medya</TabsTrigger>
          <TabsTrigger value="appearance" data-testid="tab-appearance">Görünüm</TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>Genel Ayarlar</CardTitle>
              <CardDescription>Site hakkında temel bilgiler</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="site-name">Site Adı</Label>
                <Input 
                  id="site-name" 
                  value={formData.site_name || ""}
                  onChange={(e) => setFormData({...formData, site_name: e.target.value})}
                  data-testid="site-name-input"
                />
              </div>
              <div>
                <Label htmlFor="site-desc">Site Açıklaması</Label>
                <Textarea 
                  id="site-desc" 
                  rows={3}
                  value={formData.site_description || ""}
                  onChange={(e) => setFormData({...formData, site_description: e.target.value})}
                  data-testid="site-desc-input"
                />
              </div>
              <div>
                <Label htmlFor="site-logo">Logo URL</Label>
                <Input 
                  id="site-logo" 
                  value={formData.site_logo || ""}
                  onChange={(e) => setFormData({...formData, site_logo: e.target.value})}
                  placeholder="https://..."
                  data-testid="site-logo-input"
                />
              </div>
              <div>
                <Label htmlFor="footer-text">Footer Metni</Label>
                <Input 
                  id="footer-text" 
                  value={formData.footer_text || ""}
                  onChange={(e) => setFormData({...formData, footer_text: e.target.value})}
                  data-testid="footer-text-input"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contact">
          <Card>
            <CardHeader>
              <CardTitle>İletişim Bilgileri</CardTitle>
              <CardDescription>Site iletişim bilgileri</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="contact-email">E-posta</Label>
                <Input 
                  id="contact-email" 
                  type="email"
                  value={formData.contact_email || ""}
                  onChange={(e) => setFormData({...formData, contact_email: e.target.value})}
                  data-testid="contact-email-input"
                />
              </div>
              <div>
                <Label htmlFor="contact-phone">Telefon</Label>
                <Input 
                  id="contact-phone" 
                  value={formData.contact_phone || ""}
                  onChange={(e) => setFormData({...formData, contact_phone: e.target.value})}
                  data-testid="contact-phone-input"
                />
              </div>
              <div>
                <Label htmlFor="contact-address">Adres</Label>
                <Textarea 
                  id="contact-address" 
                  rows={2}
                  value={formData.contact_address || ""}
                  onChange={(e) => setFormData({...formData, contact_address: e.target.value})}
                  data-testid="contact-address-input"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="social">
          <Card>
            <CardHeader>
              <CardTitle>Sosyal Medya</CardTitle>
              <CardDescription>Sosyal medya bağlantıları</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="social-facebook">Facebook</Label>
                <Input 
                  id="social-facebook" 
                  value={formData.social_facebook || ""}
                  onChange={(e) => setFormData({...formData, social_facebook: e.target.value})}
                  placeholder="https://facebook.com/..."
                  data-testid="social-facebook-input"
                />
              </div>
              <div>
                <Label htmlFor="social-twitter">Twitter/X</Label>
                <Input 
                  id="social-twitter" 
                  value={formData.social_twitter || ""}
                  onChange={(e) => setFormData({...formData, social_twitter: e.target.value})}
                  placeholder="https://twitter.com/..."
                  data-testid="social-twitter-input"
                />
              </div>
              <div>
                <Label htmlFor="social-instagram">Instagram</Label>
                <Input 
                  id="social-instagram" 
                  value={formData.social_instagram || ""}
                  onChange={(e) => setFormData({...formData, social_instagram: e.target.value})}
                  placeholder="https://instagram.com/..."
                  data-testid="social-instagram-input"
                />
              </div>
              <div>
                <Label htmlFor="social-linkedin">LinkedIn</Label>
                <Input 
                  id="social-linkedin" 
                  value={formData.social_linkedin || ""}
                  onChange={(e) => setFormData({...formData, social_linkedin: e.target.value})}
                  placeholder="https://linkedin.com/..."
                  data-testid="social-linkedin-input"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Görünüm Ayarları</CardTitle>
              <CardDescription>Site renk ve tema ayarları</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="primary-color">Ana Renk</Label>
                  <div className="flex gap-2">
                    <Input 
                      id="primary-color" 
                      type="color"
                      className="w-12 h-10 p-1"
                      value={formData.primary_color || "#3b82f6"}
                      onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                      data-testid="primary-color-input"
                    />
                    <Input 
                      value={formData.primary_color || "#3b82f6"}
                      onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                      className="flex-1"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="secondary-color">İkincil Renk</Label>
                  <div className="flex gap-2">
                    <Input 
                      id="secondary-color" 
                      type="color"
                      className="w-12 h-10 p-1"
                      value={formData.secondary_color || "#10b981"}
                      onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                      data-testid="secondary-color-input"
                    />
                    <Input 
                      value={formData.secondary_color || "#10b981"}
                      onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// ============ MAIN APP ============
function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Data states
  const [stats, setStats] = useState({});
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [pages, setPages] = useState([]);
  const [orders, setOrders] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [settings, setSettings] = useState({});

  // Fetch functions
  const fetchStats = useCallback(async () => {
    try {
      const data = await api.get("/dashboard/stats");
      setStats(data);
    } catch (error) {
      console.error("Stats fetch error:", error);
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      const data = await api.get("/users");
      setUsers(data);
    } catch (error) {
      console.error("Users fetch error:", error);
    }
  }, []);

  const fetchProducts = useCallback(async () => {
    try {
      const data = await api.get("/products");
      setProducts(data);
    } catch (error) {
      console.error("Products fetch error:", error);
    }
  }, []);

  const fetchPages = useCallback(async () => {
    try {
      const data = await api.get("/pages");
      setPages(data);
    } catch (error) {
      console.error("Pages fetch error:", error);
    }
  }, []);

  const fetchOrders = useCallback(async () => {
    try {
      const data = await api.get("/orders");
      setOrders(data);
    } catch (error) {
      console.error("Orders fetch error:", error);
    }
  }, []);

  const fetchCategories = useCallback(async () => {
    try {
      const data = await api.get("/categories");
      setCategories(data);
    } catch (error) {
      console.error("Categories fetch error:", error);
    }
  }, []);

  const fetchActivityLogs = useCallback(async () => {
    try {
      const data = await api.get("/activity-logs");
      setActivityLogs(data);
    } catch (error) {
      console.error("Activity logs fetch error:", error);
    }
  }, []);

  const fetchSettings = useCallback(async () => {
    try {
      const data = await api.get("/settings");
      setSettings(data);
    } catch (error) {
      console.error("Settings fetch error:", error);
    }
  }, []);

  // Initial data load and seed
  useEffect(() => {
    const initData = async () => {
      setLoading(true);
      try {
        // Try to seed data first
        await api.post("/seed-data");
      } catch (error) {
        // Data might already exist
      }
      
      // Fetch all data
      await Promise.all([
        fetchStats(),
        fetchUsers(),
        fetchProducts(),
        fetchPages(),
        fetchOrders(),
        fetchCategories(),
        fetchActivityLogs(),
        fetchSettings()
      ]);
      setLoading(false);
    };
    
    initData();
  }, [fetchStats, fetchUsers, fetchProducts, fetchPages, fetchOrders, fetchCategories, fetchActivityLogs, fetchSettings]);

  // CRUD operations
  const userOps = {
    create: (data) => api.post("/users", data),
    update: (id, data) => api.put(`/users/${id}`, data),
    delete: (id) => api.delete(`/users/${id}`)
  };

  const productOps = {
    create: (data) => api.post("/products", data),
    update: (id, data) => api.put(`/products/${id}`, data),
    delete: (id) => api.delete(`/products/${id}`)
  };

  const pageOps = {
    create: (data) => api.post("/pages", data),
    update: (id, data) => api.put(`/pages/${id}`, data),
    delete: (id) => api.delete(`/pages/${id}`)
  };

  const orderOps = {
    update: (id, data) => api.put(`/orders/${id}`, data),
    delete: (id) => api.delete(`/orders/${id}`)
  };

  const categoryOps = {
    create: (data) => api.post("/categories", data),
    delete: (id) => api.delete(`/categories/${id}`)
  };

  const settingsOps = {
    update: (data) => api.put("/settings", data)
  };

  // Render active page
  const renderPage = () => {
    switch (activeTab) {
      case "dashboard":
        return (
          <DashboardPage 
            stats={stats} 
            loading={loading} 
            onRefresh={fetchStats}
          />
        );
      case "users":
        return (
          <UsersPage 
            users={users}
            loading={loading}
            onRefresh={fetchUsers}
            onCreate={userOps.create}
            onUpdate={userOps.update}
            onDelete={userOps.delete}
          />
        );
      case "products":
        return (
          <ProductsPage 
            products={products}
            categories={categories}
            loading={loading}
            onRefresh={() => { fetchProducts(); fetchCategories(); }}
            onCreate={productOps.create}
            onUpdate={productOps.update}
            onDelete={productOps.delete}
          />
        );
      case "pages":
        return (
          <PagesPage 
            pages={pages}
            loading={loading}
            onRefresh={fetchPages}
            onCreate={pageOps.create}
            onUpdate={pageOps.update}
            onDelete={pageOps.delete}
          />
        );
      case "orders":
        return (
          <OrdersPage 
            orders={orders}
            loading={loading}
            onRefresh={fetchOrders}
            onUpdate={orderOps.update}
            onDelete={orderOps.delete}
          />
        );
      case "categories":
        return (
          <CategoriesPage 
            categories={categories}
            loading={loading}
            onRefresh={fetchCategories}
            onCreate={categoryOps.create}
            onDelete={categoryOps.delete}
          />
        );
      case "activity":
        return (
          <ActivityLogsPage 
            logs={activityLogs}
            loading={loading}
            onRefresh={fetchActivityLogs}
          />
        );
      case "settings":
        return (
          <SettingsPage 
            settings={settings}
            loading={loading}
            onUpdate={settingsOps.update}
          />
        );
      default:
        return <DashboardPage stats={stats} loading={loading} onRefresh={fetchStats} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <Toaster position="top-right" richColors />
      
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
        />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header setIsOpen={setSidebarOpen} />
          
          <main className="flex-1 overflow-y-auto p-6">
            {renderPage()}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
