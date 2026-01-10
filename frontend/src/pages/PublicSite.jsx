import { useState, useEffect } from "react";
import axios from "axios";
import { Phone, Mail, MapPin, Clock, ChevronRight, Star, Menu, X, Instagram, Facebook } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Public Site Component - Bamboo Beauty Lifes
export const PublicSite = () => {
  const [siteContent, setSiteContent] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [contactForm, setContactForm] = useState({ name: "", email: "", phone: "", message: "" });
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formSuccess, setFormSuccess] = useState(false);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      const [contentRes, settingsRes] = await Promise.all([
        axios.get(`${API}/content/all`),
        axios.get(`${API}/settings`)
      ]);
      setSiteContent(contentRes.data);
      setSettings(settingsRes.data);
    } catch (error) {
      console.error("Content fetch error:", error);
    }
    setLoading(false);
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setFormSubmitting(true);
    try {
      await axios.post(`${API}/contact`, contactForm);
      setFormSuccess(true);
      setContactForm({ name: "", email: "", phone: "", message: "" });
      setTimeout(() => setFormSuccess(false), 5000);
    } catch (error) {
      console.error("Contact form error:", error);
    }
    setFormSubmitting(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1a1a2e] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#d4a574] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white/70">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  const hero = siteContent?.hero || {};
  const services = siteContent?.services || [];
  const pricing = siteContent?.pricing || [];
  const testimonials = siteContent?.testimonials || [];
  const faqs = siteContent?.faqs || [];

  return (
    <div className="min-h-screen bg-[#1a1a2e] text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#1a1a2e]/95 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <a href="/" className="flex items-center gap-3">
              {settings?.site_logo ? (
                <img src={settings.site_logo} alt={settings?.site_name} className="h-12" />
              ) : (
                <div className="text-2xl font-serif text-[#d4a574]">
                  {settings?.site_name || "BAMBOO BEAUTY LİFES"}
                </div>
              )}
            </a>

            {/* Desktop Menu */}
            <div className="hidden lg:flex items-center gap-8">
              <a href="#hizmetler" className="text-white/80 hover:text-[#d4a574] transition-colors">HİZMETLER</a>
              <a href="#fiyatlar" className="text-white/80 hover:text-[#d4a574] transition-colors">FİYATLAR</a>
              <a href="#yorumlar" className="text-white/80 hover:text-[#d4a574] transition-colors">YORUMLAR</a>
              <a href="#iletisim" className="text-white/80 hover:text-[#d4a574] transition-colors">İLETİŞİM</a>
              <a href="/admin" className="text-white/60 hover:text-[#d4a574] transition-colors text-sm">Admin</a>
            </div>

            {/* Phone Numbers */}
            <div className="hidden lg:flex items-center gap-4">
              <a href={`tel:${settings?.contact_phone}`} className="flex items-center gap-2 text-[#d4a574]">
                <Phone className="w-4 h-4" />
                <span>{settings?.contact_phone || "0 (252) 417 23 67"}</span>
              </a>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="lg:hidden p-2 text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-[#1a1a2e] border-t border-white/10 py-4">
            <div className="flex flex-col gap-4 px-4">
              <a href="#hizmetler" className="text-white/80 hover:text-[#d4a574]" onClick={() => setMobileMenuOpen(false)}>HİZMETLER</a>
              <a href="#fiyatlar" className="text-white/80 hover:text-[#d4a574]" onClick={() => setMobileMenuOpen(false)}>FİYATLAR</a>
              <a href="#yorumlar" className="text-white/80 hover:text-[#d4a574]" onClick={() => setMobileMenuOpen(false)}>YORUMLAR</a>
              <a href="#iletisim" className="text-white/80 hover:text-[#d4a574]" onClick={() => setMobileMenuOpen(false)}>İLETİŞİM</a>
              <a href="/admin" className="text-white/60 hover:text-[#d4a574] text-sm" onClick={() => setMobileMenuOpen(false)}>Admin Panel</a>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section 
        className="relative min-h-screen flex items-center justify-center pt-20"
        style={{
          backgroundImage: hero.background_image ? `url(${hero.background_image})` : 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-black/50"></div>
        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-serif mb-6" style={{ color: hero.text_color || '#d4a574' }}>
            {hero.title || "BAMBOO BEAUTY LİFES"}
          </h1>
          <p className="text-xl md:text-2xl text-white/80 mb-4">
            {hero.subtitle || "Profesyonel Güzellik ve Bakım Merkezi"}
          </p>
          <p className="text-lg text-white/60 mb-8 max-w-2xl mx-auto">
            {hero.description || "Uzman kadromuz ve modern teknolojimizle size en iyi hizmeti sunuyoruz."}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href={hero.button_link || "#iletisim"} 
              className="px-8 py-4 bg-[#d4a574] text-[#1a1a2e] font-semibold rounded-lg hover:bg-[#c49564] transition-colors"
            >
              {hero.button_text || "Randevu Al"}
            </a>
            <a 
              href="#hizmetler" 
              className="px-8 py-4 border-2 border-[#d4a574] text-[#d4a574] font-semibold rounded-lg hover:bg-[#d4a574] hover:text-[#1a1a2e] transition-colors"
            >
              Hizmetlerimiz
            </a>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronRight className="w-8 h-8 text-[#d4a574] rotate-90" />
        </div>
      </section>

      {/* Services Section */}
      <section id="hizmetler" className="py-20 bg-[#16213e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-serif text-[#d4a574] mb-4">HİZMETLERİMİZ</h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Profesyonel ekibimiz ve modern ekipmanlarımızla size en kaliteli hizmeti sunuyoruz.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.length > 0 ? services.map((service, index) => (
              <div 
                key={service.id || index}
                className="group bg-[#1a1a2e] rounded-xl overflow-hidden hover:transform hover:scale-105 transition-all duration-300"
              >
                {service.image && (
                  <div className="relative h-48 overflow-hidden">
                    <img 
                      src={service.image} 
                      alt={service.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#1a1a2e] to-transparent"></div>
                  </div>
                )}
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-[#d4a574] mb-2">{service.title}</h3>
                  <p className="text-white/60 text-sm">{service.description}</p>
                </div>
              </div>
            )) : (
              // Default services
              [
                { title: "Cilt Bakımı", description: "Profesyonel cilt analizi ve bakım uygulamaları", image: "https://images.pexels.com/photos/3762185/pexels-photo-3762185.jpeg" },
                { title: "Lazer Epilasyon", description: "Kalıcı tüy azaltma tedavisi", image: "https://images.pexels.com/photos/5069432/pexels-photo-5069432.jpeg" },
                { title: "Masaj Terapisi", description: "Bamboo ve Hot Stone masajı", image: "https://images.pexels.com/photos/275768/pexels-photo-275768.jpeg" },
                { title: "Manikür & Pedikür", description: "El ve ayak bakımı hizmetleri", image: "https://images.pexels.com/photos/7755212/pexels-photo-7755212.jpeg" },
              ].map((service, index) => (
                <div 
                  key={index}
                  className="group bg-[#1a1a2e] rounded-xl overflow-hidden hover:transform hover:scale-105 transition-all duration-300"
                >
                  <div className="relative h-48 overflow-hidden">
                    <img 
                      src={service.image} 
                      alt={service.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#1a1a2e] to-transparent"></div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-[#d4a574] mb-2">{service.title}</h3>
                    <p className="text-white/60 text-sm">{service.description}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="fiyatlar" className="py-20 bg-[#1a1a2e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-serif text-[#d4a574] mb-4">FİYATLARIMIZ</h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Uygun fiyatlarla kaliteli hizmet anlayışımız.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricing.length > 0 ? pricing.map((plan, index) => (
              <div 
                key={plan.id || index}
                className={`relative bg-[#16213e] rounded-2xl p-8 ${plan.is_popular ? 'border-2 border-[#d4a574] transform scale-105' : 'border border-white/10'}`}
              >
                {plan.is_popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[#d4a574] text-[#1a1a2e] px-4 py-1 rounded-full text-sm font-semibold">
                    Popüler
                  </div>
                )}
                <h3 className="text-2xl font-semibold text-white mb-2">{plan.name}</h3>
                <p className="text-white/60 text-sm mb-6">{plan.description}</p>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-[#d4a574]">{plan.currency}{plan.price}</span>
                  <span className="text-white/60">/{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features?.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2 text-white/80">
                      <ChevronRight className="w-4 h-4 text-[#d4a574]" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <a 
                  href="#iletisim"
                  className={`block text-center py-3 rounded-lg font-semibold transition-colors ${
                    plan.is_popular 
                      ? 'bg-[#d4a574] text-[#1a1a2e] hover:bg-[#c49564]' 
                      : 'border border-[#d4a574] text-[#d4a574] hover:bg-[#d4a574] hover:text-[#1a1a2e]'
                  }`}
                >
                  {plan.button_text || "Randevu Al"}
                </a>
              </div>
            )) : (
              // Default pricing
              [
                { name: "Başlangıç", price: 500, description: "Temel bakım paketi", features: ["Cilt Analizi", "Yüz Temizliği", "Nemlendirme"], is_popular: false },
                { name: "Premium", price: 1500, description: "Kapsamlı bakım paketi", features: ["Cilt Analizi", "Derin Temizlik", "Anti-Aging", "Masaj", "Maske"], is_popular: true },
                { name: "VIP", price: 3000, description: "Özel VIP paketi", features: ["Tüm Premium Özellikler", "Özel Oda", "İkram", "Hediye Paketi"], is_popular: false },
              ].map((plan, index) => (
                <div 
                  key={index}
                  className={`relative bg-[#16213e] rounded-2xl p-8 ${plan.is_popular ? 'border-2 border-[#d4a574] transform scale-105' : 'border border-white/10'}`}
                >
                  {plan.is_popular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[#d4a574] text-[#1a1a2e] px-4 py-1 rounded-full text-sm font-semibold">
                      Popüler
                    </div>
                  )}
                  <h3 className="text-2xl font-semibold text-white mb-2">{plan.name}</h3>
                  <p className="text-white/60 text-sm mb-6">{plan.description}</p>
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-[#d4a574]">₺{plan.price}</span>
                    <span className="text-white/60">/seans</span>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features?.map((feature, i) => (
                      <li key={i} className="flex items-center gap-2 text-white/80">
                        <ChevronRight className="w-4 h-4 text-[#d4a574]" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <a 
                    href="#iletisim"
                    className={`block text-center py-3 rounded-lg font-semibold transition-colors ${
                      plan.is_popular 
                        ? 'bg-[#d4a574] text-[#1a1a2e] hover:bg-[#c49564]' 
                        : 'border border-[#d4a574] text-[#d4a574] hover:bg-[#d4a574] hover:text-[#1a1a2e]'
                    }`}
                  >
                    Randevu Al
                  </a>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="yorumlar" className="py-20 bg-[#16213e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-serif text-[#d4a574] mb-4">MÜŞTERİ YORUMLARI</h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Mutlu müşterilerimizin görüşleri.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.length > 0 ? testimonials.map((testimonial, index) => (
              <div 
                key={testimonial.id || index}
                className="bg-[#1a1a2e] rounded-xl p-6 border border-white/10"
              >
                <div className="flex items-center gap-4 mb-4">
                  {testimonial.avatar ? (
                    <img src={testimonial.avatar} alt={testimonial.name} className="w-14 h-14 rounded-full object-cover" />
                  ) : (
                    <div className="w-14 h-14 rounded-full bg-[#d4a574] flex items-center justify-center text-[#1a1a2e] font-bold text-xl">
                      {testimonial.name?.charAt(0)}
                    </div>
                  )}
                  <div>
                    <h4 className="font-semibold text-white">{testimonial.name}</h4>
                    <p className="text-white/60 text-sm">{testimonial.title}</p>
                  </div>
                </div>
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star 
                      key={i} 
                      className={`w-4 h-4 ${i < testimonial.rating ? 'text-[#d4a574] fill-[#d4a574]' : 'text-white/20'}`} 
                    />
                  ))}
                </div>
                <p className="text-white/70 italic">"{testimonial.content}"</p>
              </div>
            )) : (
              // Default testimonials
              [
                { name: "Ayşe Y.", title: "Düzenli Müşteri", rating: 5, content: "Harika bir deneyimdi! Personel çok ilgili ve profesyonel." },
                { name: "Mehmet K.", title: "Yeni Müşteri", rating: 5, content: "İlk ziyaretimde çok memnun kaldım. Kesinlikle tavsiye ederim." },
                { name: "Zeynep A.", title: "VIP Müşteri", rating: 5, content: "Yıllardır buraya geliyorum, kalite hiç düşmedi. Teşekkürler!" },
              ].map((testimonial, index) => (
                <div 
                  key={index}
                  className="bg-[#1a1a2e] rounded-xl p-6 border border-white/10"
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-14 h-14 rounded-full bg-[#d4a574] flex items-center justify-center text-[#1a1a2e] font-bold text-xl">
                      {testimonial.name?.charAt(0)}
                    </div>
                    <div>
                      <h4 className="font-semibold text-white">{testimonial.name}</h4>
                      <p className="text-white/60 text-sm">{testimonial.title}</p>
                    </div>
                  </div>
                  <div className="flex gap-1 mb-3">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-[#d4a574] fill-[#d4a574]" />
                    ))}
                  </div>
                  <p className="text-white/70 italic">"{testimonial.content}"</p>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      {faqs.length > 0 && (
        <section className="py-20 bg-[#1a1a2e]">
          <div className="max-w-3xl mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-serif text-[#d4a574] mb-4">SIK SORULAN SORULAR</h2>
            </div>
            <div className="space-y-4">
              {faqs.map((faq, index) => (
                <details key={faq.id || index} className="bg-[#16213e] rounded-lg border border-white/10 group">
                  <summary className="p-4 cursor-pointer flex items-center justify-between text-white font-medium">
                    {faq.question}
                    <ChevronRight className="w-5 h-5 text-[#d4a574] group-open:rotate-90 transition-transform" />
                  </summary>
                  <div className="px-4 pb-4 text-white/70">
                    {faq.answer}
                  </div>
                </details>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Contact Section */}
      <section id="iletisim" className="py-20 bg-[#16213e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-serif text-[#d4a574] mb-4">İLETİŞİM</h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Randevu almak veya bilgi almak için bize ulaşın.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Contact Info */}
            <div className="space-y-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[#d4a574] rounded-lg flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-6 h-6 text-[#1a1a2e]" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Adres</h3>
                  <p className="text-white/70">
                    {settings?.contact_address || "Tepe mahallesi Kubilay Alpuğan Sokak No:4 Daire:2, Tokgöz Apartmanı Marmaris/MUĞLA"}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[#d4a574] rounded-lg flex items-center justify-center flex-shrink-0">
                  <Phone className="w-6 h-6 text-[#1a1a2e]" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Telefon</h3>
                  <p className="text-white/70">
                    <a href={`tel:${settings?.contact_phone}`} className="hover:text-[#d4a574] transition-colors">
                      {settings?.contact_phone || "0 (252) 417 23 67"}
                    </a>
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[#d4a574] rounded-lg flex items-center justify-center flex-shrink-0">
                  <Mail className="w-6 h-6 text-[#1a1a2e]" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">E-posta</h3>
                  <p className="text-white/70">
                    <a href={`mailto:${settings?.contact_email}`} className="hover:text-[#d4a574] transition-colors">
                      {settings?.contact_email || "bamboobeautylifes@gmail.com"}
                    </a>
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-[#d4a574] rounded-lg flex items-center justify-center flex-shrink-0">
                  <Clock className="w-6 h-6 text-[#1a1a2e]" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Çalışma Saatleri</h3>
                  <p className="text-white/70">
                    Pazartesi - Cumartesi: 09:00 - 20:00<br />
                    Pazar: Kapalı
                  </p>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex gap-4 pt-4">
                {settings?.social_instagram && (
                  <a href={settings.social_instagram} target="_blank" rel="noopener noreferrer" className="w-12 h-12 bg-[#1a1a2e] rounded-lg flex items-center justify-center border border-white/10 hover:border-[#d4a574] transition-colors">
                    <Instagram className="w-5 h-5 text-[#d4a574]" />
                  </a>
                )}
                {settings?.social_facebook && (
                  <a href={settings.social_facebook} target="_blank" rel="noopener noreferrer" className="w-12 h-12 bg-[#1a1a2e] rounded-lg flex items-center justify-center border border-white/10 hover:border-[#d4a574] transition-colors">
                    <Facebook className="w-5 h-5 text-[#d4a574]" />
                  </a>
                )}
              </div>
            </div>

            {/* Contact Form */}
            <div className="bg-[#1a1a2e] rounded-2xl p-8 border border-white/10">
              <h3 className="text-2xl font-semibold text-white mb-6">Bize Ulaşın</h3>
              {formSuccess && (
                <div className="mb-6 p-4 bg-green-500/20 border border-green-500/50 rounded-lg text-green-400">
                  Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.
                </div>
              )}
              <form onSubmit={handleContactSubmit} className="space-y-4">
                <div>
                  <input
                    type="text"
                    placeholder="Adınız Soyadınız"
                    value={contactForm.name}
                    onChange={(e) => setContactForm({...contactForm, name: e.target.value})}
                    required
                    className="w-full px-4 py-3 bg-[#16213e] border border-white/10 rounded-lg text-white placeholder-white/40 focus:border-[#d4a574] focus:outline-none transition-colors"
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <input
                    type="email"
                    placeholder="E-posta"
                    value={contactForm.email}
                    onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                    required
                    className="w-full px-4 py-3 bg-[#16213e] border border-white/10 rounded-lg text-white placeholder-white/40 focus:border-[#d4a574] focus:outline-none transition-colors"
                  />
                  <input
                    type="tel"
                    placeholder="Telefon"
                    value={contactForm.phone}
                    onChange={(e) => setContactForm({...contactForm, phone: e.target.value})}
                    className="w-full px-4 py-3 bg-[#16213e] border border-white/10 rounded-lg text-white placeholder-white/40 focus:border-[#d4a574] focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <textarea
                    placeholder="Mesajınız"
                    value={contactForm.message}
                    onChange={(e) => setContactForm({...contactForm, message: e.target.value})}
                    required
                    rows={4}
                    className="w-full px-4 py-3 bg-[#16213e] border border-white/10 rounded-lg text-white placeholder-white/40 focus:border-[#d4a574] focus:outline-none transition-colors resize-none"
                  ></textarea>
                </div>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="w-full py-4 bg-[#d4a574] text-[#1a1a2e] font-semibold rounded-lg hover:bg-[#c49564] transition-colors disabled:opacity-50"
                >
                  {formSubmitting ? "Gönderiliyor..." : "GÖNDER"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-[#1a1a2e] border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-white/60 text-sm">
              {settings?.footer_text || "© 2025 BAMBOO BEAUTY LİFES. Tüm hakları saklıdır."}
            </p>
            <div className="flex items-center gap-4">
              <a href="/admin" className="text-white/40 hover:text-[#d4a574] text-sm transition-colors">
                Admin Panel
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PublicSite;
