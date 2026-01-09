import { useState, useEffect } from "react";
import { 
  Plus, Edit, Trash2, RefreshCw, Image, Type, Palette,
  Eye, EyeOff, Save, X, Upload, Link, Star, Quote,
  BarChart3, HelpCircle, Menu as MenuIcon, FileText, Megaphone
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
import { Switch } from "@/components/ui/switch";
import { toast } from 'sonner';

// ============ HERO SECTION MANAGER ============
export const HeroManager = ({ api }) => {
  const [hero, setHero] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchHero();
  }, []);

  const fetchHero = async () => {
    try {
      const data = await api.get("/content/hero");
      setHero(data);
    } catch (error) {
      console.error("Hero fetch error:", error);
    }
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put("/content/hero", hero);
      toast.success("Hero bölümü güncellendi");
    } catch (error) {
      toast.error("Güncelleme başarısız");
    }
    setSaving(false);
  };

  if (loading) return <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Hero Bölümü</h2>
          <p className="text-slate-500">Ana sayfanın üst kısmını düzenleyin</p>
        </div>
        <Button onClick={handleSave} disabled={saving} data-testid="save-hero-btn">
          {saving ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
          Kaydet
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Type className="w-5 h-5" /> Metin İçerikleri</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Ana Başlık</Label>
              <Input 
                value={hero?.title || ""} 
                onChange={(e) => setHero({...hero, title: e.target.value})}
                data-testid="hero-title"
              />
            </div>
            <div>
              <Label>Alt Başlık</Label>
              <Input 
                value={hero?.subtitle || ""} 
                onChange={(e) => setHero({...hero, subtitle: e.target.value})}
                data-testid="hero-subtitle"
              />
            </div>
            <div>
              <Label>Açıklama</Label>
              <Textarea 
                rows={3}
                value={hero?.description || ""} 
                onChange={(e) => setHero({...hero, description: e.target.value})}
                data-testid="hero-description"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Buton Metni</Label>
                <Input 
                  value={hero?.button_text || ""} 
                  onChange={(e) => setHero({...hero, button_text: e.target.value})}
                  data-testid="hero-button-text"
                />
              </div>
              <div>
                <Label>Buton Linki</Label>
                <Input 
                  value={hero?.button_link || ""} 
                  onChange={(e) => setHero({...hero, button_link: e.target.value})}
                  data-testid="hero-button-link"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Palette className="w-5 h-5" /> Görsel Ayarları</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Arka Plan Resmi (URL)</Label>
              <Input 
                value={hero?.background_image || ""} 
                onChange={(e) => setHero({...hero, background_image: e.target.value})}
                placeholder="https://..."
                data-testid="hero-bg-image"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Arka Plan Rengi</Label>
                <div className="flex gap-2">
                  <Input 
                    type="color"
                    className="w-12 h-10 p-1"
                    value={hero?.background_color || "#1e293b"}
                    onChange={(e) => setHero({...hero, background_color: e.target.value})}
                  />
                  <Input 
                    value={hero?.background_color || "#1e293b"}
                    onChange={(e) => setHero({...hero, background_color: e.target.value})}
                    className="flex-1"
                  />
                </div>
              </div>
              <div>
                <Label>Yazı Rengi</Label>
                <div className="flex gap-2">
                  <Input 
                    type="color"
                    className="w-12 h-10 p-1"
                    value={hero?.text_color || "#ffffff"}
                    onChange={(e) => setHero({...hero, text_color: e.target.value})}
                  />
                  <Input 
                    value={hero?.text_color || "#ffffff"}
                    onChange={(e) => setHero({...hero, text_color: e.target.value})}
                    className="flex-1"
                  />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Switch 
                checked={hero?.is_active ?? true}
                onCheckedChange={(checked) => setHero({...hero, is_active: checked})}
              />
              <Label>Aktif</Label>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Eye className="w-5 h-5" /> Önizleme</CardTitle>
        </CardHeader>
        <CardContent>
          <div 
            className="rounded-lg p-8 text-center"
            style={{ 
              backgroundColor: hero?.background_color || "#1e293b",
              backgroundImage: hero?.background_image ? `url(${hero.background_image})` : 'none',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              color: hero?.text_color || "#ffffff"
            }}
          >
            <h1 className="text-3xl font-bold mb-2">{hero?.title || "Başlık"}</h1>
            <p className="text-xl mb-2 opacity-90">{hero?.subtitle || "Alt Başlık"}</p>
            <p className="mb-4 opacity-80">{hero?.description || "Açıklama"}</p>
            <Button>{hero?.button_text || "Buton"}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============ SERVICES MANAGER ============
export const ServicesManager = ({ api }) => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [formData, setFormData] = useState({
    title: "", description: "", icon: "star", image: "", link: "", order: 0, is_active: true
  });

  const icons = ["star", "globe", "smartphone", "shopping-cart", "search", "megaphone", "headphones", "heart", "zap", "shield", "award", "gift"];

  useEffect(() => { fetchServices(); }, []);

  const fetchServices = async () => {
    try {
      const data = await api.get("/content/services");
      setServices(data);
    } catch (error) {
      console.error("Services fetch error:", error);
    }
    setLoading(false);
  };

  const openModal = (service = null) => {
    if (service) {
      setEditingService(service);
      setFormData({ ...service });
    } else {
      setEditingService(null);
      setFormData({ title: "", description: "", icon: "star", image: "", link: "", order: services.length, is_active: true });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingService) {
        await api.put(`/content/services/${editingService.id}`, formData);
        toast.success("Hizmet güncellendi");
      } else {
        await api.post("/content/services", formData);
        toast.success("Hizmet oluşturuldu");
      }
      setIsModalOpen(false);
      fetchServices();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu hizmeti silmek istediğinize emin misiniz?")) {
      try {
        await api.delete(`/content/services/${id}`);
        toast.success("Hizmet silindi");
        fetchServices();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Hizmetler</h2>
          <p className="text-slate-500">Sunduğunuz hizmetleri yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-service-btn">
          <Plus className="w-4 h-4 mr-2" /> Yeni Hizmet
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((service) => (
            <Card key={service.id} className={!service.is_active ? "opacity-50" : ""}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                      <Star className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{service.title}</h3>
                      <p className="text-sm text-slate-500 line-clamp-2">{service.description}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => openModal(service)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(service.id)}>
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                {!service.is_active && <Badge variant="secondary" className="mt-2">Pasif</Badge>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingService ? "Hizmet Düzenle" : "Yeni Hizmet"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Başlık</Label>
              <Input value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
            </div>
            <div>
              <Label>Açıklama</Label>
              <Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>İkon</Label>
                <Select value={formData.icon} onValueChange={(v) => setFormData({...formData, icon: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {icons.map(icon => <SelectItem key={icon} value={icon}>{icon}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Sıra</Label>
                <Input type="number" value={formData.order} onChange={(e) => setFormData({...formData, order: parseInt(e.target.value) || 0})} />
              </div>
            </div>
            <div>
              <Label>Görsel URL (Opsiyonel)</Label>
              <Input value={formData.image || ""} onChange={(e) => setFormData({...formData, image: e.target.value})} />
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={formData.is_active} onCheckedChange={(checked) => setFormData({...formData, is_active: checked})} />
              <Label>Aktif</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit}>Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ PRICING MANAGER ============
export const PricingManager = ({ api }) => {
  const [pricing, setPricing] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPricing, setEditingPricing] = useState(null);
  const [formData, setFormData] = useState({
    name: "", price: 0, currency: "₺", period: "ay", description: "",
    features: [], is_popular: false, button_text: "Satın Al", order: 0, is_active: true
  });
  const [newFeature, setNewFeature] = useState("");

  useEffect(() => { fetchPricing(); }, []);

  const fetchPricing = async () => {
    try {
      const data = await api.get("/content/pricing");
      setPricing(data);
    } catch (error) {
      console.error("Pricing fetch error:", error);
    }
    setLoading(false);
  };

  const openModal = (item = null) => {
    if (item) {
      setEditingPricing(item);
      setFormData({ ...item });
    } else {
      setEditingPricing(null);
      setFormData({
        name: "", price: 0, currency: "₺", period: "ay", description: "",
        features: [], is_popular: false, button_text: "Satın Al", order: pricing.length, is_active: true
      });
    }
    setIsModalOpen(true);
  };

  const addFeature = () => {
    if (newFeature.trim()) {
      setFormData({...formData, features: [...formData.features, newFeature.trim()]});
      setNewFeature("");
    }
  };

  const removeFeature = (index) => {
    setFormData({...formData, features: formData.features.filter((_, i) => i !== index)});
  };

  const handleSubmit = async () => {
    try {
      if (editingPricing) {
        await api.put(`/content/pricing/${editingPricing.id}`, formData);
        toast.success("Fiyat kartı güncellendi");
      } else {
        await api.post("/content/pricing", formData);
        toast.success("Fiyat kartı oluşturuldu");
      }
      setIsModalOpen(false);
      fetchPricing();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu fiyat kartını silmek istediğinize emin misiniz?")) {
      try {
        await api.delete(`/content/pricing/${id}`);
        toast.success("Fiyat kartı silindi");
        fetchPricing();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Fiyatlandırma</h2>
          <p className="text-slate-500">Fiyat paketlerinizi yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-pricing-btn">
          <Plus className="w-4 h-4 mr-2" /> Yeni Paket
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pricing.map((item) => (
            <Card key={item.id} className={`${!item.is_active ? "opacity-50" : ""} ${item.is_popular ? "border-blue-500 border-2" : ""}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    {item.is_popular && <Badge className="mb-2 bg-blue-500">Popüler</Badge>}
                    <h3 className="font-bold text-lg">{item.name}</h3>
                    <p className="text-2xl font-bold text-blue-600">
                      {item.currency}{item.price.toLocaleString('tr-TR')}
                      <span className="text-sm text-slate-500">/{item.period}</span>
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => openModal(item)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(item.id)}>
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-slate-500 mb-2">{item.description}</p>
                <ul className="text-sm space-y-1">
                  {item.features?.slice(0, 3).map((f, i) => (
                    <li key={i} className="text-slate-600">✓ {f}</li>
                  ))}
                  {item.features?.length > 3 && <li className="text-slate-400">+{item.features.length - 3} daha</li>}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingPricing ? "Fiyat Kartı Düzenle" : "Yeni Fiyat Kartı"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Paket Adı</Label>
                <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <Label>Fiyat</Label>
                <Input type="number" value={formData.price} onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value) || 0})} />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>Para Birimi</Label>
                <Select value={formData.currency} onValueChange={(v) => setFormData({...formData, currency: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="₺">₺ TL</SelectItem>
                    <SelectItem value="$">$ USD</SelectItem>
                    <SelectItem value="€">€ EUR</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Periyot</Label>
                <Select value={formData.period} onValueChange={(v) => setFormData({...formData, period: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ay">Aylık</SelectItem>
                    <SelectItem value="yıl">Yıllık</SelectItem>
                    <SelectItem value="tek seferlik">Tek Seferlik</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Sıra</Label>
                <Input type="number" value={formData.order} onChange={(e) => setFormData({...formData, order: parseInt(e.target.value) || 0})} />
              </div>
            </div>
            <div>
              <Label>Açıklama</Label>
              <Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
            </div>
            <div>
              <Label>Özellikler</Label>
              <div className="flex gap-2 mb-2">
                <Input value={newFeature} onChange={(e) => setNewFeature(e.target.value)} placeholder="Yeni özellik ekle" />
                <Button type="button" onClick={addFeature}><Plus className="w-4 h-4" /></Button>
              </div>
              <div className="space-y-1">
                {formData.features?.map((f, i) => (
                  <div key={i} className="flex items-center justify-between bg-slate-50 px-2 py-1 rounded">
                    <span className="text-sm">{f}</span>
                    <button onClick={() => removeFeature(i)} className="text-red-500"><X className="w-4 h-4" /></button>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Switch checked={formData.is_popular} onCheckedChange={(checked) => setFormData({...formData, is_popular: checked})} />
                <Label>Popüler</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={formData.is_active} onCheckedChange={(checked) => setFormData({...formData, is_active: checked})} />
                <Label>Aktif</Label>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit}>Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ TESTIMONIALS MANAGER ============
export const TestimonialsManager = ({ api }) => {
  const [testimonials, setTestimonials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    name: "", title: "", content: "", avatar: "", rating: 5, order: 0, is_active: true
  });

  useEffect(() => { fetchTestimonials(); }, []);

  const fetchTestimonials = async () => {
    try {
      const data = await api.get("/content/testimonials");
      setTestimonials(data);
    } catch (error) {
      console.error("Testimonials fetch error:", error);
    }
    setLoading(false);
  };

  const openModal = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({ ...item });
    } else {
      setEditingItem(null);
      setFormData({ name: "", title: "", content: "", avatar: "", rating: 5, order: testimonials.length, is_active: true });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await api.put(`/content/testimonials/${editingItem.id}`, formData);
        toast.success("Referans güncellendi");
      } else {
        await api.post("/content/testimonials", formData);
        toast.success("Referans oluşturuldu");
      }
      setIsModalOpen(false);
      fetchTestimonials();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu referansı silmek istediğinize emin misiniz?")) {
      try {
        await api.delete(`/content/testimonials/${id}`);
        toast.success("Referans silindi");
        fetchTestimonials();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Müşteri Yorumları</h2>
          <p className="text-slate-500">Müşteri referanslarını yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-testimonial-btn">
          <Plus className="w-4 h-4 mr-2" /> Yeni Referans
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {testimonials.map((item) => (
            <Card key={item.id} className={!item.is_active ? "opacity-50" : ""}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {item.avatar ? (
                      <img src={item.avatar} alt={item.name} className="w-10 h-10 rounded-full object-cover" />
                    ) : (
                      <div className="w-10 h-10 bg-slate-200 rounded-full flex items-center justify-center">
                        <Quote className="w-5 h-5 text-slate-500" />
                      </div>
                    )}
                    <div>
                      <h3 className="font-semibold">{item.name}</h3>
                      <p className="text-sm text-slate-500">{item.title}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => openModal(item)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(item.id)}>
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-slate-600 line-clamp-3">"{item.content}"</p>
                <div className="mt-2 text-yellow-500">
                  {"★".repeat(item.rating)}{"☆".repeat(5 - item.rating)}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingItem ? "Referans Düzenle" : "Yeni Referans"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Ad Soyad</Label>
                <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <Label>Ünvan / Şirket</Label>
                <Input value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
              </div>
            </div>
            <div>
              <Label>Yorum</Label>
              <Textarea rows={3} value={formData.content} onChange={(e) => setFormData({...formData, content: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Avatar URL</Label>
                <Input value={formData.avatar || ""} onChange={(e) => setFormData({...formData, avatar: e.target.value})} placeholder="https://..." />
              </div>
              <div>
                <Label>Puan (1-5)</Label>
                <Select value={String(formData.rating)} onValueChange={(v) => setFormData({...formData, rating: parseInt(v)})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {[1,2,3,4,5].map(n => <SelectItem key={n} value={String(n)}>{n} Yıldız</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={formData.is_active} onCheckedChange={(checked) => setFormData({...formData, is_active: checked})} />
              <Label>Aktif</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit}>Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ BANNERS MANAGER ============
export const BannersManager = ({ api }) => {
  const [banners, setBanners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    title: "", subtitle: "", image: "", link: "", button_text: "", order: 0, is_active: true
  });

  useEffect(() => { fetchBanners(); }, []);

  const fetchBanners = async () => {
    try {
      const data = await api.get("/content/banners");
      setBanners(data);
    } catch (error) {
      console.error("Banners fetch error:", error);
    }
    setLoading(false);
  };

  const openModal = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({ ...item });
    } else {
      setEditingItem(null);
      setFormData({ title: "", subtitle: "", image: "", link: "", button_text: "", order: banners.length, is_active: true });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await api.put(`/content/banners/${editingItem.id}`, formData);
        toast.success("Banner güncellendi");
      } else {
        await api.post("/content/banners", formData);
        toast.success("Banner oluşturuldu");
      }
      setIsModalOpen(false);
      fetchBanners();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu banner'ı silmek istediğinize emin misiniz?")) {
      try {
        await api.delete(`/content/banners/${id}`);
        toast.success("Banner silindi");
        fetchBanners();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Bannerlar</h2>
          <p className="text-slate-500">Slider ve banner görsellerini yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-banner-btn">
          <Plus className="w-4 h-4 mr-2" /> Yeni Banner
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {banners.map((item) => (
            <Card key={item.id} className={!item.is_active ? "opacity-50" : ""}>
              <CardContent className="p-0">
                <div className="relative">
                  <img src={item.image} alt={item.title} className="w-full h-40 object-cover rounded-t-lg" />
                  <div className="absolute inset-0 bg-black/40 rounded-t-lg flex items-center justify-center">
                    <div className="text-center text-white p-4">
                      <h3 className="font-bold text-lg">{item.title}</h3>
                      {item.subtitle && <p className="text-sm opacity-90">{item.subtitle}</p>}
                    </div>
                  </div>
                  <div className="absolute top-2 right-2 flex gap-1">
                    <Button variant="secondary" size="icon" onClick={() => openModal(item)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="secondary" size="icon" onClick={() => handleDelete(item.id)}>
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                <div className="p-3">
                  <div className="flex items-center justify-between">
                    <Badge variant={item.is_active ? "default" : "secondary"}>{item.is_active ? "Aktif" : "Pasif"}</Badge>
                    <span className="text-sm text-slate-500">Sıra: {item.order}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingItem ? "Banner Düzenle" : "Yeni Banner"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Başlık</Label>
              <Input value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
            </div>
            <div>
              <Label>Alt Başlık</Label>
              <Input value={formData.subtitle || ""} onChange={(e) => setFormData({...formData, subtitle: e.target.value})} />
            </div>
            <div>
              <Label>Görsel URL</Label>
              <Input value={formData.image} onChange={(e) => setFormData({...formData, image: e.target.value})} placeholder="https://..." />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Link</Label>
                <Input value={formData.link || ""} onChange={(e) => setFormData({...formData, link: e.target.value})} />
              </div>
              <div>
                <Label>Buton Metni</Label>
                <Input value={formData.button_text || ""} onChange={(e) => setFormData({...formData, button_text: e.target.value})} />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={formData.is_active} onCheckedChange={(checked) => setFormData({...formData, is_active: checked})} />
              <Label>Aktif</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit}>Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ MEDIA LIBRARY ============
export const MediaLibrary = ({ api }) => {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: "", url: "", type: "image", alt_text: "", category: "" });

  useEffect(() => { fetchMedia(); }, []);

  const fetchMedia = async () => {
    try {
      const data = await api.get("/content/media");
      setMedia(data);
    } catch (error) {
      console.error("Media fetch error:", error);
    }
    setLoading(false);
  };

  const handleSubmit = async () => {
    try {
      await api.post("/content/media", formData);
      toast.success("Medya eklendi");
      setIsModalOpen(false);
      setFormData({ name: "", url: "", type: "image", alt_text: "", category: "" });
      fetchMedia();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu medyayı silmek istediğinize emin misiniz?")) {
      try {
        await api.delete(`/content/media/${id}`);
        toast.success("Medya silindi");
        fetchMedia();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  const copyUrl = (url) => {
    navigator.clipboard.writeText(url);
    toast.success("URL kopyalandı");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Medya Kütüphanesi</h2>
          <p className="text-slate-500">Görsel ve dosyalarınızı yönetin</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} data-testid="add-media-btn">
          <Plus className="w-4 h-4 mr-2" /> Medya Ekle
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {media.map((item) => (
            <Card key={item.id} className="group relative overflow-hidden">
              <CardContent className="p-0">
                <img src={item.url} alt={item.alt_text || item.name} className="w-full h-32 object-cover" />
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <Button variant="secondary" size="icon" onClick={() => copyUrl(item.url)}>
                    <Link className="w-4 h-4" />
                  </Button>
                  <Button variant="secondary" size="icon" onClick={() => handleDelete(item.id)}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
                <div className="p-2">
                  <p className="text-xs truncate">{item.name}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Medya Ekle</DialogTitle>
            <DialogDescription>Görsel URL'si ekleyin</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Ad</Label>
              <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
            </div>
            <div>
              <Label>URL</Label>
              <Input value={formData.url} onChange={(e) => setFormData({...formData, url: e.target.value})} placeholder="https://..." />
            </div>
            <div>
              <Label>Alt Metin</Label>
              <Input value={formData.alt_text || ""} onChange={(e) => setFormData({...formData, alt_text: e.target.value})} />
            </div>
            <div>
              <Label>Kategori</Label>
              <Input value={formData.category || ""} onChange={(e) => setFormData({...formData, category: e.target.value})} placeholder="örn: hero, products" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit}>Ekle</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============ FAQ MANAGER ============
export const FAQManager = ({ api }) => {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    question: "", answer: "", category: "", order: 0, is_active: true
  });

  useEffect(() => { fetchFaqs(); }, []);

  const fetchFaqs = async () => {
    try {
      const data = await api.get("/content/faqs");
      setFaqs(data);
    } catch (error) {
      console.error("FAQs fetch error:", error);
    }
    setLoading(false);
  };

  const openModal = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({ ...item });
    } else {
      setEditingItem(null);
      setFormData({ question: "", answer: "", category: "", order: faqs.length, is_active: true });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingItem) {
        await api.put(`/content/faqs/${editingItem.id}`, formData);
        toast.success("SSS güncellendi");
      } else {
        await api.post("/content/faqs", formData);
        toast.success("SSS oluşturuldu");
      }
      setIsModalOpen(false);
      fetchFaqs();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Bir hata oluştu");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bu SSS'yi silmek istediğinize emin misiniz?")) {
      try {
        await api.delete(`/content/faqs/${id}`);
        toast.success("SSS silindi");
        fetchFaqs();
      } catch (error) {
        toast.error("Silme işlemi başarısız");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">Sıkça Sorulan Sorular</h2>
          <p className="text-slate-500">SSS içeriklerini yönetin</p>
        </div>
        <Button onClick={() => openModal()} data-testid="add-faq-btn">
          <Plus className="w-4 h-4 mr-2" /> Yeni SSS
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><RefreshCw className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="space-y-3">
          {faqs.map((item) => (
            <Card key={item.id} className={!item.is_active ? "opacity-50" : ""}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <HelpCircle className="w-5 h-5 text-blue-500 mt-0.5" />
                    <div>
                      <h3 className="font-medium">{item.question}</h3>
                      <p className="text-sm text-slate-500 mt-1">{item.answer}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => openModal(item)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(item.id)}>
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingItem ? "SSS Düzenle" : "Yeni SSS"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Soru</Label>
              <Input value={formData.question} onChange={(e) => setFormData({...formData, question: e.target.value})} />
            </div>
            <div>
              <Label>Cevap</Label>
              <Textarea rows={4} value={formData.answer} onChange={(e) => setFormData({...formData, answer: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Kategori</Label>
                <Input value={formData.category || ""} onChange={(e) => setFormData({...formData, category: e.target.value})} />
              </div>
              <div>
                <Label>Sıra</Label>
                <Input type="number" value={formData.order} onChange={(e) => setFormData({...formData, order: parseInt(e.target.value) || 0})} />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={formData.is_active} onCheckedChange={(checked) => setFormData({...formData, is_active: checked})} />
              <Label>Aktif</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>İptal</Button>
            <Button onClick={handleSubmit}>Kaydet</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
