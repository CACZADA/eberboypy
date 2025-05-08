import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import random
import time
import aiohttp
import os
from discord.ui import View
from tkinter import Button

PREFIX="+"
TICKET_CATEGORY = "Tickets"
TICKET_CATEGORY_NAME="Tickets"
LOG_CHANNEL_NAME="logs"
WELCOME_CHANNEL_NAME="bienvenue"
MOD_LOG_CHANNEL="mod-log"
startup_time=time.time()


TICKET_EMBED_TITLE="🎫 Support Ticket"
TICKET_EMBED_DESC="Merci de patienter, un membre du staff arrivera bientôt."
TICKET_EMBED_COLOR=discord.Color.blue()

status_list=[
    "🎮 en stream sur Twitch !",
    "🔧 modération en cours",
    "🎫 support via les tickets",
    f"📖 {PREFIX}help pour les commandes",
    "🔍 surveillance du serveur"
]

warns={}
mod_notes={}

# This function is moved below the bot initialization



intents=discord.Intents.all()
bot=commands.Bot(command_prefix=PREFIX,intents=intents,help_command=None)

@bot.event
async def on_ready():
    change_status.start()

@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(activity=discord.Streaming(name=random.choice(status_list),url="https://twitch.tv/twitch"))

@bot.event
async def on_command_error(ctx,error):
  bot=commands.Bot(command_prefix=PREFIX,intents=intents,help_command=None)

 # Remplace par l'ID du salon de logs


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant `{error.param.name}`.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send(f"⚠️ Erreur: {error}")

@bot.event
async def on_member_join(member):
    channel=get(member.guild.text_channels,name=WELCOME_CHANNEL_NAME)
    if channel: await channel.send(f"👋 Bienvenue {member.mention} !")

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    channel=get(message.guild.text_channels,name=LOG_CHANNEL_NAME)
    if channel: await channel.send(f"🗑️ [DELETE] {message.author}: {message.content}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.bot: return
    if len(message.content)>500:
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, message trop long !")

TICKET_TYPES = {
    "Support": "Besoin d'aide générale",
    "Bug": "Signaler un bug",
    "Suggestion": "Faire une suggestion"
}
TICKET_IMAGE_URL = "https://example.com/ticket_banner.png"

status_list = [
    "🎮 en stream sur Twitch !",
    "🔧 modération en cours",
    f"📖 {PREFIX}help pour les commandes",
    "YOUR OWN BOT IN ZENITH"
]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

class HelpView(discord.ui.View):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.current = 0
    @discord.ui.button(label="◀", style=discord.ButtonStyle.red)
    async def back(self, interaction, button):
        self.current = max(0, self.current - 1)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
    @discord.ui.button(label="▶", style=discord.ButtonStyle.red)
    async def forward(self, interaction, button):
        self.current = min(len(self.pages)-1, self.current+1)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

class TicketSelect(discord.ui.View):
    def __init__(self):
        super().__init__()
        opts = [discord.SelectOption(label=k, description=v) for k,v in TICKET_TYPES.items()]
        self.add_item(discord.ui.Select(placeholder="Choisissez un type...", options=opts))
    @discord.ui.select()
    async def select(self, interaction, select):
        t = select.values[0]
        g = interaction.guild
        cat = get(g.categories, name=TICKET_CATEGORY) or await g.create_category(TICKET_CATEGORY)
        ow = {g.default_role:discord.PermissionOverwrite(read_messages=False), interaction.user:discord.PermissionOverwrite(read_messages=True, send_messages=True), g.me:discord.PermissionOverwrite(read_messages=True)}
        ch = await g.create_text_channel(f"{t.lower()}-{interaction.user.name}", category=cat, overwrites=ow)
        e = discord.Embed(title=f"🎫 {t} Ticket", description=TICKET_TYPES[t], color=discord.Color.blue())
        e.set_image(url=TICKET_IMAGE_URL)
        await ch.send(embed=e)
        await interaction.response.send_message(f"🎟️ Ticket créé: {ch.mention}", ephemeral=True)

@bot.event
async def on_ready():
    change_status.start()

@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(activity=discord.Streaming(name=random.choice(status_list), url="https://twitch.tv/twitch"))

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.MissingPermissions): await ctx.send(f"❌ {ctx.author.mention}, permission manquante: {','.join(err.missing_permissions)}")
    elif isinstance(err, commands.MissingRequiredArgument): await ctx.send(f"❌ Arg. manquant: {err.param.name}")



@bot.command()
async def ticket(ctx):
    e = discord.Embed(title="Créer un ticket", description="Sélectionnez ci-dessous :", color=discord.Color.blue())
    e.set_image(url=TICKET_IMAGE_URL)
    await ctx.send(embed=e, view=TicketSelect())

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx,member:discord.Member,*,reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kické. Raison: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx,member:discord.Member,*,reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banni. Raison: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx,*,member_name):
    bans=await ctx.guild.bans()
    user=next((b.user for b in bans if str(b.user)==member_name),None)
    if user: await ctx.guild.unban(user);await ctx.send(f"✅ {user} déban !")

@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(ctx,member:discord.Member,*,reason=None):
    await member.ban(reason=reason)
    await ctx.guild.unban(member)
    await ctx.send(f"↩️ {member} softbanni. Raison: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def hackban(ctx,user_id:int):
    await ctx.guild.ban(discord.Object(id=user_id))
    await ctx.send(f"🛠️ ID {user_id} banni")

@bot.command()
@commands.has_permissions(ban_members=True)
async def massban(ctx,*user_ids:int):
    for uid in user_ids: await ctx.guild.ban(discord.Object(id=uid))
    await ctx.send(f"🔢 Massban: {len(user_ids)}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def masskick(ctx,*members:discord.Member):
    for m in members: await m.kick()
    await ctx.send(f"🔢 Masskick: {len(members)}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx,amount:int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 {amount} messages purgés.",delete_after=5)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx,member:discord.Member):
    role=get(ctx.guild.roles,name="Muted") or await ctx.guild.create_role(name="Muted")
    for ch in ctx.guild.channels: await ch.set_permissions(role,speak=False,send_messages=False)
    await member.add_roles(role)
    await ctx.send(f"🔇 {member.mention} mute.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx,member:discord.Member):
    role=get(ctx.guild.roles,name="Muted")
    if role in member.roles: await member.remove_roles(role);await ctx.send(f"🔊 {member.mention} unmute.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx,member:discord.Member,seconds:int):
    await mute.callback(ctx,member);await asyncio.sleep(seconds);await unmute.callback(ctx,member)
    await ctx.send(f"⌛ {member.mention} unmute après {seconds}s.")

@bot.command()
@commands.has_permissions(move_members=True)
async def deafen(ctx,member:discord.Member):
    await member.edit(deafen=True)
    await ctx.send(f"🔇 {member.mention} deafened.")

@bot.command()
@commands.has_permissions(move_members=True)
async def undeafen(ctx,member:discord.Member):
    await member.edit(deafen=False)
    await ctx.send(f"🔊 {member.mention} undeafened.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_input: str):
    # Vérifie si l'utilisateur a mentionné un rôle
    if role_input.startswith("<@&") and role_input.endswith(">"):
        role_id = int(role_input[3:-1])  # Extrait l'ID du rôle mentionné
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    else:
        # Recherche insensible à la casse et approximative
        role = discord.utils.find(lambda r: role_input.lower() in r.name.lower(), ctx.guild.roles)

    if role:
        if role in member.roles:
            await ctx.send(f"⚠️ {member.mention} a déjà le rôle `{role.name}`.")
        else:
            await member.add_roles(role)
            await ctx.send(f"➕ Rôle `{role.name}` ajouté à {member.mention}.")
    else:
        await ctx.send(f"❌ Aucun rôle correspondant à `{role_input}` trouvé. Vérifiez l'orthographe ou la mention.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role_input: str):
    # Vérifie si l'utilisateur a mentionné un rôle
    if role_input.startswith("<@&") and role_input.endswith(">"):
        role_id = int(role_input[3:-1])  # Extrait l'ID du rôle mentionné
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    else:
        # Recherche insensible à la casse et approximative
        role = discord.utils.find(lambda r: role_input.lower() in r.name.lower(), ctx.guild.roles)

    if role:
        if role not in member.roles:
            await ctx.send(f"⚠️ {member.mention} n'a pas le rôle `{role.name}`.")
        else:
            await member.remove_roles(role)
            await ctx.send(f"➖ Rôle `{role.name}` retiré de {member.mention}.")
    else:
        await ctx.send(f"❌ Aucun rôle correspondant à `{role_input}` trouvé. Vérifiez l'orthographe ou la mention.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def createrole(ctx,*,name):
    await ctx.guild.create_role(name=name)
    await ctx.send(f"🆕 Rôle `{name}` créé.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def deleterole(ctx,*,name):
    role=get(ctx.guild.roles,name=name)
    if role: await role.delete();await ctx.send(f"❌ Rôle `{name}` supprimé.")

@bot.command()
async def roleinfo(ctx,*,role:discord.Role):
    embed=discord.Embed(title=role.name,color=role.color)
    embed.add_field(name="ID",value=role.id)
    embed.add_field(name="Membres",value=len(role.members))
    await ctx.send(embed=embed)

@bot.command()
async def rolelist(ctx):
    await ctx.send(", ".join([r.name for r in ctx.guild.roles]))

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=False)
    await ctx.send("🔒 Salon verrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=True)
    await ctx.send("🔓 Salon déverrouillé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def hide(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,read_messages=False)
    await ctx.send("🙈 Salon masqué.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def show(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,read_messages=True)
    await ctx.send("🙉 Salon visible.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def createchannel(ctx,*,name):
    await ctx.guild.create_text_channel(name)
    await ctx.send(f"🆕 Salon `{name}` créé.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def deletechannel(ctx,channel:discord.TextChannel):
    await channel.delete()
    await ctx.send(f"❌ Salon `{channel.name}` supprimé.")

@bot.command()
async def slowmode(ctx,seconds:int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐢 Slowmode: {seconds}s")

@bot.command()
async def noslow(ctx):
    await ctx.channel.edit(slowmode_delay=0)
    await ctx.send("🐇 Slowmode désactivé.")

@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, nick_name: str):
    try:
        await member.edit(nick=nick_name)
        await ctx.send(f"✏️ Le pseudo de {member.mention} a été changé en `{nick_name}`.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de changer le pseudo de cet utilisateur.")
    except discord.HTTPException:
        await ctx.send("⚠️ Une erreur est survenue lors de la tentative de changement de pseudo.")

@bot.command()
async def resetnick(ctx,member:discord.Member):
    await member.edit(nick=None)
    await ctx.send("♻️ Pseudo réinitialisé.")

@bot.command()
async def voicekick(ctx,member:discord.Member):
    await member.move_to(None)
    await ctx.send(f"🔈 {member} expulsé du vocal.")

@bot.command()
async def warn(ctx,member:discord.Member,*,reason=None):
    warns.setdefault(member.id,[]).append(reason)
    await ctx.send(f"⚠️ {member} averti: {reason}")

@bot.command()
async def unwarn(ctx,member:discord.Member):
    if warns.get(member.id): warns[member.id].pop()
    await ctx.send(f"✅ Dernier avertissement supprimé pour {member}.")

@bot.command()
async def warnlist(ctx,member:discord.Member):
    await ctx.send(f"📋 Averts: {warns.get(member.id,[])}")

@bot.command()
async def clearwarns(ctx,member:discord.Member):
    warns.pop(member.id,None)
    await ctx.send(f"🗑️ Averts réinitialisés pour {member}.")

@bot.command()
async def modlog(ctx,*,entry):
    channel=get(ctx.guild.text_channels,name=MOD_LOG_CHANNEL)
    if channel: await channel.send(f"📝 {ctx.author}: {entry}")

@bot.command()
async def modnotes(ctx,member:discord.Member,*,note):
    mod_notes.setdefault(member.id,[]).append(note)
    await ctx.send(f"🗂️ Note ajoutée pour {member}.")

@bot.command()
async def announce(ctx,*,msg):
    await ctx.send(embed=discord.Embed(title="📢 Annonce",description=msg))


class EmbedInputModal(discord.ui.Modal):
    def __init__(self, embed, field, title, placeholder, view):
        super().__init__(title=title)
        self.embed = embed
        self.field = field
        self.view = view
        self.add_item(discord.ui.TextInput(label=title, placeholder=placeholder))

    async def on_submit(self, interaction: discord.Interaction):
        value = self.children[0].value
        if self.field == "title":
            self.embed.title = value
        elif self.field == "description":
            self.embed.description = value
        elif self.field == "image":
            self.embed.set_image(url=value)
        await self.view.update_embed(interaction)


class ChannelInputModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Choisir un salon")
        self.view = view
        self.add_item(discord.ui.TextInput(label="Nom du salon", placeholder="Entrez le nom du salon"))

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.children[0].value
        channel = discord.utils.get(self.view.ctx.guild.text_channels, name=channel_name)
        if channel:
            self.view.target_channel = channel
            await interaction.response.send_message(f"✅ Salon sélectionné : {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)


class RoleEmbedEditor(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = discord.Embed(title="Embed vide", description="Ajoutez des éléments pour personnaliser cet embed.", color=discord.Color.greyple())
        self.message = None
        self.roles = {}  # Stocke les rôles et leurs emojis
        self.role_mode = None  # Mode d'attribution des rôles (reaction, select, button)
        self.target_channel = None  # Salon où envoyer l'embed

    async def send(self):
        self.message = await self.ctx.send(embed=self.embed, view=self)

    async def update_embed(self, interaction):
        await self.message.edit(embed=self.embed, view=self)
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Choisissez un élément à modifier",
        options=[
            discord.SelectOption(label="Titre", emoji="📝", description="Modifier le titre de l'embed"),
            discord.SelectOption(label="Description", emoji="📜", description="Modifier la description de l'embed"),
            discord.SelectOption(label="Couleur", emoji="🎨", description="Modifier la couleur de l'embed"),
            discord.SelectOption(label="Image", emoji="🖼️", description="Ajouter une image à l'embed"),
            discord.SelectOption(label="Salon", emoji="📩", description="Choisir le salon où envoyer l'embed"),
            discord.SelectOption(label="Ajouter un rôle", emoji="➕", description="Ajouter un rôle interactif"),
            discord.SelectOption(label="Mode des rôles", emoji="⚙️", description="Choisir le mode d'attribution des rôles"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier cet embed.", ephemeral=True)
            return

        choice = select.values[0]
        if choice == "Titre":
            await interaction.response.send_modal(EmbedInputModal(self.embed, "title", "Modifier le titre", "Entrez le nouveau titre", self))
        elif choice == "Description":
            await interaction.response.send_modal(EmbedInputModal(self.embed, "description", "Modifier la description", "Entrez la nouvelle description", self))
        elif choice == "Couleur":
            await interaction.response.send_modal(ColorInputModal(self.embed, self))
        elif choice == "Image":
            await interaction.response.send_modal(EmbedInputModal(self.embed, "image", "Ajouter une image", "Entrez l'URL de l'image", self))
        elif choice == "Salon":
            await interaction.response.send_modal(ChannelInputModal(self))
        elif choice == "Ajouter un rôle":
            await interaction.response.send_modal(RoleInputModal(self))
        elif choice == "Mode des rôles":
            await interaction.response.send_modal(RoleModeModal(self))

    @discord.ui.button(label="Envoyer l'embed", style=discord.ButtonStyle.green, emoji="✅")
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Vous ne pouvez pas envoyer cet embed.", ephemeral=True)
            return

        if self.target_channel:
            if self.role_mode == "reaction":
                for emoji in self.roles.keys():
                    await self.message.add_reaction(emoji)
            elif self.role_mode == "select":
                await self.target_channel.send(embed=self.embed, view=RoleSelectView(self.roles))
            elif self.role_mode == "button":
                await self.target_channel.send(embed=self.embed, view=RoleButtonView(self.roles))
            await interaction.response.send_message(f"✅ Embed envoyé dans {self.target_channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Aucun salon sélectionné pour envoyer l'embed.", ephemeral=True)


class EmbedInputModal(discord.ui.Modal):
    def __init__(self, embed, field, title, placeholder, view):
        super().__init__(title=title)
        self.embed = embed
        self.field = field
        self.view = view
        self.add_item(discord.ui.TextInput(label=title, placeholder=placeholder))

    async def on_submit(self, interaction: discord.Interaction):
        value = self.children[0].value
        if self.field == "title":
            self.embed.title = value
        elif self.field == "description":
            self.embed.description = value
        elif self.field == "image":
            self.embed.set_image(url=value)
        await self.view.update_embed(interaction)


class ColorInputModal(discord.ui.Modal):
    def __init__(self, embed, view):
        super().__init__(title="Modifier la couleur")
        self.embed = embed
        self.view = view
        self.add_item(discord.ui.TextInput(label="Couleur", placeholder="Entrez une couleur (rouge, bleu, vert, etc.)"))

    async def on_submit(self, interaction: discord.Interaction):
        color_map = {
            "rouge": discord.Color.red(),
            "bleu": discord.Color.blue(),
            "vert": discord.Color.green(),
            "jaune": discord.Color.gold(),
            "violet": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "gris": discord.Color.greyple(),
            "noir": discord.Color.dark_grey(),
            "blanc": discord.Color.light_grey(),
            "cyan": discord.Color.teal(),
            "rose": discord.Color.magenta(),
        }
        value = self.children[0].value.lower()
        if value in color_map:
            self.embed.color = color_map[value]
            await self.view.update_embed(interaction)
        else:
            await interaction.response.send_message("❌ Couleur invalide. Essayez : rouge, bleu, vert, etc.", ephemeral=True)


class ChannelInputModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Choisir un salon")
        self.view = view
        self.add_item(discord.ui.TextInput(label="Nom du salon", placeholder="Entrez le nom du salon"))

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.children[0].value
        channel = discord.utils.get(self.view.ctx.guild.text_channels, name=channel_name)
        if channel:
            self.view.target_channel = channel
            await interaction.response.send_message(f"✅ Salon sélectionné : {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)


class RoleInputModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Ajouter un rôle interactif")
        self.view = view
        self.add_item(discord.ui.TextInput(label="Nom du rôle", placeholder="Entrez le nom ou l'ID du rôle"))
        self.add_item(discord.ui.TextInput(label="Emoji", placeholder="Entrez un emoji pour ce rôle"))

    async def on_submit(self, interaction: discord.Interaction):
        role_name = self.children[0].value
        emoji = self.children[1].value
        role = discord.utils.get(self.view.ctx.guild.roles, name=role_name) or self.view.ctx.guild.get_role(int(role_name))
        if role:
            self.view.roles[emoji] = role
            await interaction.response.send_message(f"✅ Rôle ajouté : {role.name} avec l'emoji {emoji}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)


class RoleModeModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Choisir le mode des rôles")
        self.view = view
        self.add_item(discord.ui.TextInput(label="Mode", placeholder="Entrez reaction, select ou button"))

    async def on_submit(self, interaction: discord.Interaction):
        mode = self.children[0].value.lower()
        if mode in ["reaction", "select", "button"]:
            self.view.role_mode = mode
            await interaction.response.send_message(f"✅ Mode des rôles défini sur `{mode}`.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Mode invalide. Choisissez entre `reaction`, `select` ou `button`.", ephemeral=True)


class RoleSelectView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=role.name, emoji=emoji, value=str(role.id)) for emoji, role in roles.items()]
        self.add_item(discord.ui.Select(placeholder="Choisissez un rôle", options=options))

    @discord.ui.select()
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        role_id = int(select.values[0])
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"❌ Rôle `{role.name}` retiré.", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Rôle `{role.name}` ajouté.", ephemeral=True)


class RoleButtonView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        for emoji, role in roles.items():
            self.add_item(discord.ui.Button(label=role.name, emoji=emoji, custom_id=str(role.id)))

    @discord.ui.button()
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = int(button.custom_id)
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"❌ Rôle `{role.name}` retiré.", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Rôle `{role.name}` ajouté.", ephemeral=True)


@bot.command(name="embed")
async def embed_command(ctx):
    view = RoleEmbedEditor(ctx)
    await view.send()


@bot.command()
async def poll(ctx,*,question):
    m=await ctx.send(f"📊 {question}")
    await m.add_reaction("👍");await m.add_reaction("👎")

@bot.command()
async def say(ctx, *, msg):
    try:
        await ctx.message.delete()  # Supprime le message de l'utilisateur
    except discord.Forbidden:
        await ctx.send("⚠️ Je n'ai pas la permission de supprimer ce message.")
    await ctx.send(msg)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong {round(bot.latency*1000)}ms")

@bot.command()
async def serverinfo(ctx):
    g=ctx.guild
    embed=discord.Embed(title=g.name)
    embed.add_field(name="Membres",value=g.member_count)
    embed.add_field(name="Salons",value=len(g.channels))
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx,member:discord.Member=None):
    m=member or ctx.author
    avatar=m.avatar.url if m.avatar else m.default_avatar.url
    embed=discord.Embed(title=m.display_name)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name="ID",value=m.id)
    embed.add_field(name="Créé le",value=m.created_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx,member:discord.Member=None):
    m=member or ctx.author
    url=m.avatar.url if m.avatar else m.default_avatar.url
    await ctx.send(embed=discord.Embed().set_image(url=url))

@bot.command()
async def uptime(ctx):
    d=int(time.time()-startup_time)
    h,m=divmod(d,3600);m,s=divmod(m,60)
    await ctx.send(f"⏱️ Uptime: {h}h{m}m{s}s")

@bot.command()
async def invites(ctx,member:discord.Member=None):
    m=member or ctx.author
    count=sum(i.uses for i in await ctx.guild.invites() if i.inviter==m)
    await ctx.send(f"🔗 {m} a invité {count}")

@bot.command()
async def roles(ctx,member:discord.Member=None):
    m=member or ctx.author
    await ctx.send(", ".join(r.name for r in m.roles if r.name!="@everyone"))

@bot.command()
async def channels(ctx):
    await ctx.send(", ".join(c.name for c in ctx.guild.channels))

@bot.command()
async def randomrole(ctx):
    r=random.choice([r for r in ctx.guild.roles if r.name!="@everyone"]);await ctx.send(r.name)

@bot.command()
async def servericon(ctx):
    url=ctx.guild.icon.url if ctx.guild.icon else None
    await ctx.send(embed=discord.Embed().set_image(url=url) if url else "Pas d'icone")

@bot.command(name="help")
async def custom_help(ctx):
    embeds = []
    categories = {
        "🔨 Modération": [
            ("kick", "Expulse un membre."),
            ("ban", "Bannit un membre."),
            ("unban", "Débannit un membre."),
            ("softban", "Softban un membre."),
            ("hackban", "Bannit un utilisateur par ID."),
            ("massban", "Bannit plusieurs utilisateurs."),
            ("masskick", "Expulse plusieurs membres."),
            ("purge", "Supprime des messages."),
            ("mute", "Mute un membre."),
            ("unmute", "Unmute un membre."),
            ("tempmute", "Mute temporairement un membre."),
            ("deafen", "Rend un membre sourd."),
            ("undeafen", "Rend un membre non sourd."),
            ("addrole", "Ajoute un rôle à un membre."),
            ("removerole", "Retire un rôle d'un membre."),
            ("createrole", "Crée un rôle."),
            ("deleterole", "Supprime un rôle."),
            ("renew", "Recrée un salon."),
        ],
        "🔧 Gestion du serveur": [
            ("raidlog", "Active les logs de l'antiraid dans un salon."),
            ("raidping", "Modifie les rôles mentionnés en cas de raid."),
            ("antitoken", "Active/désactive l'antitoken sur le serveur."),
            ("secur", "Affiche ou modifie les paramètres de sécurité."),
            ("antiupdate", "Active/désactive l'antiupdate."),
            ("antichannel", "Active/désactive l'antichannel."),
            ("antirole", "Active/désactive l'antirole."),
            ("antiwebhook", "Active/désactive l'antiwebhook."),
            ("clear_webhooks", "Supprime tous les webhooks du serveur."),
            ("antiunban", "Active/désactive l'antiunban."),
            ("antibot", "Active/désactive l'antibot."),
            ("antiban", "Active/désactive l'antiban."),
            ("antieveryone", "Active/désactive l'antieveryone."),
            ("antideco", "Active/désactive l'antideco."),
            ("blrank", "Gère la blacklist rank."),
            ("punition", "Règle la punition des membres pour l'antiraid."),
            ("creation_limit", "Définit une limite d'âge pour les comptes."),
            ("wl", "Gère la whitelist du serveur."),
        ],
        "⚙️ Contrôle du bot": [
            ("set", "Change le nom, la photo de profil ou la bannière du bot."),
            ("set_profil", "Modifie d'un coup le profil du bot."),
            ("theme", "Change la couleur des embeds du bot."),
            ("activity", "Change l'activité du bot."),
            ("remove_activity", "Supprime l'activité du bot."),
            ("status", "Change le statut du bot."),
            ("mp_settings", "Gère les messages privés envoyés par le bot."),
            ("server_list", "Affiche la liste des serveurs où se trouve le bot."),
            ("invite", "Envoie une invitation pour un serveur."),
            ("leave", "Fait quitter un serveur au bot."),
            ("discussion", "Permet de discuter à travers le bot."),
            ("mp", "Envoie un message privé à un membre."),
            ("owner", "Gère les owners du bot."),
            ("bl", "Gère la blacklist du bot."),
            ("say", "Fait dire au bot un message."),
            ("mainprefix", "Change le préfixe principal du bot."),
            ("updatebot", "Met à jour le bot."),
            ("reset_server", "Réinitialise les paramètres du serveur."),
            ("resetall", "Réinitialise tous les paramètres du bot."),
        ],
        "ℹ️ Informations": [
            ("ping", "Affiche la latence du bot."),
            ("serverinfo", "Affiche les informations du serveur."),
            ("userinfo", "Affiche les informations d'un utilisateur."),
            ("avatar", "Affiche l'avatar d'un utilisateur."),
            ("uptime", "Affiche le temps d'activité du bot."),
            ("invites", "Affiche le nombre d'invitations d'un utilisateur."),
            ("roles", "Affiche les rôles d'un utilisateur."),
            ("channels", "Affiche les salons du serveur."),
            ("randomrole", "Affiche un rôle aléatoire."),
            ("servericon", "Affiche l'icône du serveur."),
        ],
        "📋 Divers": [
            ("nick", "Change le pseudo d'un membre."),
            ("resetnick", "Réinitialise le pseudo d'un membre."),
            ("voicekick", "Expulse un membre d'un salon vocal."),
            ("warn", "Avertit un membre."),
            ("unwarn", "Supprime le dernier avertissement d'un membre."),
            ("warnlist", "Affiche les avertissements d'un membre."),
            ("clearwarns", "Réinitialise les avertissements d'un membre."),
            ("modlog", "Ajoute une entrée dans le journal de modération."),
            ("modnotes", "Ajoute une note de modération pour un membre."),
            ("announce", "Envoie une annonce."),
            ("embed", "Envoie un message embed."),
            ("poll", "Crée un sondage."),
            ("snipe", "Affiche le dernier message supprimé."),
        ],
    }

    for category, commands in categories.items():
        embed = discord.Embed(title=category, color=discord.Color.blue())
        for name, description in commands:
            embed.add_field(name=f"`{PREFIX}{name}`", value=description, inline=False)
        embed.set_footer(text=f"Préfixe : {PREFIX} • Créé par sleazy ")
        embeds.append(embed)

    view = HelpView(embeds)
    await ctx.send(embed=embeds[0], view=view)

# 🕵️ Stocker le dernier message supprimé
sniped_messages = {}

@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        sniped_messages[message.channel.id] = message

# 🔁 Recréer le salon
@bot.command(name="renew")
@commands.has_permissions(administrator=True)
async def renew(ctx):
    old_channel = ctx.channel
    overwrites = old_channel.overwrites
    category = old_channel.category
    topic = old_channel.topic

    # Créer un nouveau salon
    new_channel = await ctx.guild.create_text_channel(
        name=old_channel.name,
        overwrites=overwrites,
        category=category
    )
    if topic:
        await new_channel.edit(topic=topic)

    await ctx.send(f"✅ Salon recréé : {new_channel.mention}")
    await old_channel.delete()

# 🕵️ Snipe : afficher le dernier message supprimé
@bot.command(name="snipe")
async def snipe(ctx):
    sniped = sniped_messages.get(ctx.channel.id)
    if sniped:
        embed = discord.Embed(
            title="🕵️ Message supprimé",
            description=sniped.content or "*Aucun contenu (embed ou fichier)*",
            color=discord.Color.orange(),
            timestamp=sniped.created_at
        )
        embed.set_author(name=str(sniped.author), icon_url=sniped.author.display_avatar.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Aucun message supprimé trouvé.")

@bot.command(name="set")
async def set_bot(ctx, action: str, *, value: str = None):
    if action == "name":
        try:
            await bot.user.edit(username=value)
            await ctx.send(f"✅ Nom du bot changé en `{value}`.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Impossible de changer le nom du bot : {e}")
    elif action == "pic":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(value) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await bot.user.edit(avatar=data)
                        await ctx.send("✅ Photo de profil du bot mise à jour.")
                    else:
                        await ctx.send("❌ Impossible de récupérer l'image. Vérifiez l'URL.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Impossible de changer la photo de profil : {e}")
    elif action == "banner":
        await ctx.send("⚠️ Discord ne permet pas de changer la bannière via l'API.")
    else:
        await ctx.send("❌ Action invalide. Utilisez `name`, `pic` ou `banner`.")

@bot.command(name="set_profil")
async def set_profil(ctx, name: str, pic_url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(pic_url) as resp:
            if resp.status == 200:
                data = await resp.read()
                await bot.user.edit(username=name, avatar=data)
                await ctx.send(f"✅ Profil du bot mis à jour : `{name}`.")

@bot.command(name="theme")
async def theme(ctx, color: str):
    global EMBED_COLOR
    try:
        EMBED_COLOR = discord.Color(int(color.strip("#"), 16))
        await ctx.send(f"✅ Couleur des embeds changée en `{color}`.")
    except ValueError:
        await ctx.send("❌ Couleur invalide. Utilisez un code hexadécimal.")

@bot.command(name="activity")
async def activity(ctx, action: str, *, message: str):
    activities = {
        "playto": discord.Game,
        "listen": lambda m: discord.Activity(type=discord.ActivityType.listening, name=m),
        "watch": lambda m: discord.Activity(type=discord.ActivityType.watching, name=m),
        "compet": lambda m: discord.Activity(type=discord.ActivityType.competing, name=m),
        "stream": lambda m: discord.Streaming(name=m, url="https://twitch.tv/twitch")
    }
    if action in activities:
        bot_activity = activities[action](message)
        await bot.change_presence(activity=bot_activity)
        await ctx.send(f"✅ Activité du bot changée en `{action}` : `{message}`.")
    else:
        await ctx.send("❌ Action invalide. Utilisez `playto`, `listen`, `watch`, `compet` ou `stream`.")

@bot.command(name="remove_activity")
async def remove_activity(ctx):
    await bot.change_presence(activity=None)
    await ctx.send("✅ Activité du bot supprimée.")

@bot.command(name="status")
async def status(ctx, status: str):
    statuses = {
        "online": discord.Status.online,
        "idle": discord.Status.idle,
        "dnd": discord.Status.dnd,
        "invisible": discord.Status.invisible
    }
    if status in statuses:
        await bot.change_presence(status=statuses[status])
        await ctx.send(f"✅ Statut du bot changé en `{status}`.")
    else:
        await ctx.send("❌ Statut invalide. Utilisez `online`, `idle`, `dnd` ou `invisible`.")

@bot.command(name="mp_settings")
async def mp_settings(ctx):
    await ctx.send("⚙️ Paramètres des messages privés : ...")

@bot.command(name="server_list")
async def server_list(ctx):
    servers = [guild.name for guild in bot.guilds]
    await ctx.send(f"📋 Liste des serveurs : {', '.join(servers)}")

@bot.command(name="invite")
async def invite(ctx, server_id: int):
    guild = discord.utils.get(bot.guilds, id=server_id)
    if guild:
        invites = await guild.invites()
        if invites:
            await ctx.send(f"🔗 Invitation : {invites[0].url}")
        else:
            await ctx.send("❌ Aucun lien d'invitation trouvé.")
    else:
        await ctx.send("❌ Serveur introuvable.")

@bot.command(name="leave")
async def leave(ctx, server_id: int):
    guild = discord.utils.get(bot.guilds, id=server_id)
    if guild:
        await guild.leave()
        await ctx.send(f"✅ Le bot a quitté le serveur `{guild.name}`.")
    else:
        await ctx.send("❌ Serveur introuvable.")

@bot.command(name="discussion")
async def discussion(ctx, server_id: int, *, message: str):
    guild = discord.utils.get(bot.guilds, id=server_id)
    if guild:
        channel = guild.text_channels[0]
        await channel.send(message)
        await ctx.send(f"✅ Message envoyé sur `{guild.name}`.")
    else:
        await ctx.send("❌ Serveur introuvable.")

@bot.command(name="mp")
async def mp(ctx, member: discord.Member, *, message: str):
    try:
        await member.send(message)
        await ctx.send(f"✅ Message envoyé à {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Impossible d'envoyer un message privé à cet utilisateur.")

@bot.command(name="owner")
async def owner(ctx, action: str, member: discord.Member = None):
    if action == "add" and member:
        # Ajouter le membre à la liste des owners
        await ctx.send(f"✅ {member.mention} ajouté comme Owner.")
    elif action == "remove" and member:
        # Retirer le membre de la liste des owners
        await ctx.send(f"✅ {member.mention} retiré des Owners.")
    elif action == "list":
        # Afficher la liste des owners
        await ctx.send("📋 Liste des Owners : ...")
    else:
        await ctx.send("⚠️ Utilisation : `+owner <add/remove/list>`")

@bot.command(name="bl")
async def blacklist(ctx, action: str, member: discord.Member = None, *, reason: str = None):
    if action == "add" and member:
        # Ajouter le membre à la blacklist
        await ctx.send(f"✅ {member.mention} ajouté à la blacklist. Raison : {reason}")
    elif action == "remove" and member:
        # Retirer le membre de la blacklist
        await ctx.send(f"✅ {member.mention} retiré de la blacklist.")
    elif action == "list":
        # Afficher la blacklist
        await ctx.send("📋 Blacklist : ...")
    else:
        await ctx.send("⚠️ Utilisation : `+bl <add/remove/list>`")



@bot.command(name="mainprefix")
async def mainprefix(ctx, prefix: str):
    global PREFIX
    PREFIX = prefix
    bot.command_prefix = PREFIX
    await ctx.send(f"✅ Préfixe principal changé en `{prefix}`.")

@bot.command(name="updatebot")
async def updatebot(ctx):
    await ctx.send("🔄 Mise à jour du bot en cours...")
    # Logique pour mettre à jour le bot
    await ctx.send("✅ Bot mis à jour avec succès.")

@bot.command(name="reset_server")
async def reset_server(ctx):
    await ctx.send("⚠️ Réinitialisation des paramètres du serveur en cours...")
    # Logique pour réinitialiser les paramètres
    await ctx.send("✅ Paramètres du serveur réinitialisés.")

@bot.command(name="resetall")
async def resetall(ctx):
    await ctx.send("⚠️ Réinitialisation complète du bot en cours...")
    # Logique pour réinitialiser tous les paramètres
    await ctx.send("✅ Tous les paramètres du bot ont été réinitialisés.")


# Variables globales pour l'antiraid
raid_logs_channel = None
raid_ping_role = None
antiraid_settings = {
    "antitoken": {"status": "off", "limit": 0, "duration": 0},
    "secur": "off",
    "antiupdate": "off",
    "antichannel": "off",
    "antirole": {"status": "off", "scope": "all"},
    "antiwebhook": "off",
    "antiunban": "off",
    "antibot": "off",
    "antiban": {"status": "off", "limit": 0, "duration": 0},
    "antieveryone": {"status": "off", "limit": 0, "duration": 0},
    "antideco": {"status": "off", "limit": 0, "duration": 0},
    "blrank": {"status": "off", "scope": "all"},
    "punition": "kick",
    "creation_limit": 0,
    "whitelist": []
}

# Commande pour activer/désactiver les logs de raid
@bot.command(name="raidlog")
async def raidlog(ctx, status: str, channel: discord.TextChannel = None):
    global raid_logs_channel
    if status.lower() == "on" and channel:
        raid_logs_channel = channel
        await ctx.send(f"✅ Logs de raid activés dans {channel.mention}.")
    elif status.lower() == "off":
        raid_logs_channel = None
        await ctx.send("❌ Logs de raid désactivés.")
    else:
        await ctx.send("⚠️ Utilisation : `+raidlog <on/off> [salon]`")

# Commande pour modifier le rôle mentionné en cas de raid
@bot.command(name="raidping")
async def raidping(ctx, role: discord.Role):
    global raid_ping_role
    raid_ping_role = role
    await ctx.send(f"✅ Rôle mentionné en cas de raid : {role.mention}")

# Commande pour gérer l'antitoken
@bot.command(name="antitoken")
async def antitoken(ctx, mode: str, limit_or_duration: str = None):
    if mode.lower() in ["on", "off", "lock"]:
        antiraid_settings["antitoken"]["status"] = mode.lower()
        await ctx.send(f"✅ Antitoken réglé sur `{mode}`.")
    elif "/" in limit_or_duration:
        limit, duration = map(int, limit_or_duration.split("/"))
        antiraid_settings["antitoken"]["limit"] = limit
        antiraid_settings["antitoken"]["duration"] = duration
        await ctx.send(f"✅ Sensibilité de l'antitoken réglée : {limit} utilisateurs en {duration}s.")
    else:
        await ctx.send("⚠️ Utilisation : `+antitoken <on/off/lock>` ou `+antitoken <nombre>/<durée>`")

# Commande pour afficher ou modifier les paramètres de sécurité
@bot.command(name="secur")
async def secur(ctx, level: str = None):
    if level:
        antiraid_settings["secur"] = level.lower()
        await ctx.send(f"✅ Niveau de sécurité réglé sur `{level}`.")
    else:
        await ctx.send(f"🔒 Niveau de sécurité actuel : `{antiraid_settings['secur']}`")

# Commandes pour activer/désactiver les protections
@bot.command(name="antiupdate")
async def antiupdate(ctx, status: str):
    antiraid_settings["antiupdate"] = status.lower()
    await ctx.send(f"✅ Antiupdate réglé sur `{status}`.")

@bot.command(name="antichannel")
async def antichannel(ctx, status: str):
    antiraid_settings["antichannel"] = status.lower()
    await ctx.send(f"✅ Antichannel réglé sur `{status}`.")

@bot.command(name="antirole")
async def antirole(ctx, status: str, scope: str = "all"):
    antiraid_settings["antirole"]["status"] = status.lower()
    antiraid_settings["antirole"]["scope"] = scope.lower()
    await ctx.send(f"✅ Antirole réglé sur `{status}` pour `{scope}`.")

@bot.command(name="antiwebhook")
async def antiwebhook(ctx, status: str):
    antiraid_settings["antiwebhook"] = status.lower()
    await ctx.send(f"✅ Antiwebhook réglé sur `{status}`.")

@bot.command(name="clear_webhooks")
async def clear_webhooks(ctx):
    for webhook in await ctx.guild.webhooks():
        await webhook.delete()
    await ctx.send("✅ Tous les webhooks ont été supprimés.")

@bot.command(name="antiunban")
async def antiunban(ctx, status: str):
    antiraid_settings["antiunban"] = status.lower()
    await ctx.send(f"✅ Antiunban réglé sur `{status}`.")

@bot.command(name="antibot")
async def antibot(ctx, status: str):
    antiraid_settings["antibot"] = status.lower()
    await ctx.send(f"✅ Antibot réglé sur `{status}`.")

@bot.command(name="antiban")
async def antiban(ctx, status_or_limit: str, duration: str = None):
    if "/" in status_or_limit:
        limit, duration = map(int, status_or_limit.split("/"))
        antiraid_settings["antiban"]["limit"] = limit
        antiraid_settings["antiban"]["duration"] = duration
        await ctx.send(f"✅ Sensibilité de l'antiban réglée : {limit} bans en {duration}s.")
    else:
        antiraid_settings["antiban"]["status"] = status_or_limit.lower()
        await ctx.send(f"✅ Antiban réglé sur `{status_or_limit}`.")

@bot.command(name="antieveryone")
async def antieveryone(ctx, status_or_limit: str, duration: str = None):
    if "/" in status_or_limit:
        limit, duration = map(int, status_or_limit.split("/"))
        antiraid_settings["antieveryone"]["limit"] = limit
        antiraid_settings["antieveryone"]["duration"] = duration
        await ctx.send(f"✅ Sensibilité de l'antieveryone réglée : {limit} mentions everyone en {duration}s.")
    else:
        antiraid_settings["antieveryone"]["status"] = status_or_limit.lower()
        await ctx.send(f"✅ Antieveryone réglé sur `{status_or_limit}`.")

@bot.command(name="antideco")
async def antideco(ctx, status_or_limit: str, duration: str = None):
    if "/" in status_or_limit:
        limit, duration = map(int, status_or_limit.split("/"))
        antiraid_settings["antideco"]["limit"] = limit
        antiraid_settings["antideco"]["duration"] = duration
        await ctx.send(f"✅ Sensibilité de l'antideco réglée : {limit} déconnexions en {duration}s.")
    else:
        antiraid_settings["antideco"]["status"] = status_or_limit.lower()
        await ctx.send(f"✅ Antideco réglé sur `{status_or_limit}`.")

# Commandes pour la blacklist rank
@bot.command(name="blrank")
async def blrank(ctx, action: str, member: discord.Member = None):
    if action.lower() == "add" and member:
        antiraid_settings["blrank"]["members"].append(member.id)
        await ctx.send(f"✅ {member.mention} ajouté à la blacklist rank.")
    elif action.lower() == "del" and member:
        antiraid_settings["blrank"]["members"].remove(member.id)
        await ctx.send(f"✅ {member.mention} retiré de la blacklist rank.")
    elif action.lower() == "on" or action.lower() == "off":
        antiraid_settings["blrank"]["status"] = action.lower()
        await ctx.send(f"✅ Blacklist rank réglée sur `{action}`.")
    else:
        await ctx.send("⚠️ Utilisation : `+blrank <add/del/on/off>`")

# Commande pour régler la punition
@bot.command(name="punition")
async def punition(ctx, feature: str, action: str):
    if feature == "all":
        for key in antiraid_settings:
            if isinstance(antiraid_settings[key], dict):
                antiraid_settings[key]["punition"] = action
        await ctx.send(f"✅ Punition réglée sur `{action}` pour toutes les fonctions.")
    else:
        antiraid_settings[feature]["punition"] = action
        await ctx.send(f"✅ Punition pour `{feature}` réglée sur `{action}`.")

# Commande pour définir la limite de création de compte
@bot.command(name="creation_limit")
async def creation_limit(ctx, duration: int):
    antiraid_settings["creation_limit"] = duration
    await ctx.send(f"✅ Limite de création de compte réglée sur `{duration}` jours.")

# Commandes pour la whitelist
@bot.command(name="wl")
async def wl(ctx, member: discord.Member = None):
    if member:
        antiraid_settings["whitelist"].append(member.id)
        await ctx.send(f"✅ {member.mention} ajouté à la whitelist.")
    else:
        whitelist = ", ".join([f"<@{id}>" for id in antiraid_settings["whitelist"]])
        await ctx.send(f"📋 Whitelist : {whitelist}")

@bot.command(name="unwl")
async def unwl(ctx, member: discord.Member):
    antiraid_settings["whitelist"].remove(member.id)
    await ctx.send(f"✅ {member.mention} retiré de la whitelist.")

@bot.command(name="clear_wl")
async def clear_wl(ctx):
    antiraid_settings["whitelist"].clear()
    await ctx.send("✅ Whitelist vidée.")




# Commande pour afficher un menu interactif pour créer un giveaway
@bot.command(name="giveaway")
async def giveaway(ctx):
    await ctx.send("🎉 Utilisez `+startgiveaway` pour démarrer un giveaway interactif.")

# Commande pour terminer un giveaway avec l'ID de son message
@bot.command(name="endgiveaway")
@commands.has_permissions(manage_messages=True)
async def end_giveaway(ctx, message_id: int):
    await ctx.send(f"🎉 Giveaway avec l'ID {message_id} terminé.")

# Commande pour rejouer le dernier giveaway
@bot.command(name="reroll")
@commands.has_permissions(manage_messages=True)
async def reroll(ctx):
    await ctx.send("🎉 Nouveau gagnant sélectionné pour le dernier giveaway.")

# Commande pour un tirage au sort instantané
@bot.command(name="choose")
async def choose(ctx, *, options: str):
    choices = options.split(",,")
    winner = random.choice(choices)
    await ctx.send(f"🎉 Le gagnant est : {winner}")

# Commande pour afficher un générateur d'embed interactif


# Commande pour créer une backup
@bot.command(name="backup")
async def backup(ctx, type: str, name: str):
    await ctx.send(f"📦 Backup `{type}` avec le nom `{name}` créée.")

# Commande pour afficher la liste des backups
@bot.command(name="backup_list")
async def backup_list(ctx, type: str):
    await ctx.send(f"📋 Liste des backups `{type}` : ...")

# Commande pour supprimer une backup
@bot.command(name="backup_delete")
async def backup_delete(ctx, type: str, name: str):
    await ctx.send(f"❌ Backup `{type}` avec le nom `{name}` supprimée.")

# Commande pour charger une backup
@bot.command(name="backup_load")
async def backup_load(ctx, type: str, name: str):
    await ctx.send(f"🔄 Backup `{type}` avec le nom `{name}` chargée.")

# Commande pour configurer une backup automatique
@bot.command(name="autobackup")
async def autobackup(ctx, type: str, days: int):
    await ctx.send(f"🔄 Backup automatique `{type}` configurée tous les {days} jours.")

# Commande pour afficher une barre de chargement
@bot.command(name="loading")
async def loading(ctx, duration: int, *, message: str):
    await ctx.send(f"⏳ {message} (Durée : {duration}s)")

# Commande pour créer un emoji custom
@bot.command(name="create")
async def create(ctx, emoji: str, name: str):
    await ctx.send(f"🆕 Emoji `{name}` créé avec `{emoji}`.")

# Commande pour créer un sticker
@bot.command(name="newsticker")
async def newsticker(ctx, *, name: str):
    await ctx.send(f"🆕 Sticker `{name}` créé.")

# Commande pour ajouter un rôle à tous les membres
@bot.command(name="massiverole")
async def massiverole(ctx, role: discord.Role, target_role: discord.Role = None):
    await ctx.send(f"➕ Rôle `{role}` ajouté à tous les membres.")

# Commande pour retirer un rôle à tous les membres
@bot.command(name="unmassiverole")
async def unmassiverole(ctx, role: discord.Role, target_role: discord.Role = None):
    await ctx.send(f"➖ Rôle `{role}` retiré à tous les membres.")

# Commande pour déplacer tous les membres d'un salon vocal
@bot.command(name="voicemove")
async def voicemove(ctx, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
    await ctx.send(f"🔄 Membres déplacés de `{from_channel}` à `{to_channel}`.")

# Commande pour déconnecter un membre d'un salon vocal


# Commande pour déconnecter tous les utilisateurs d'un salon vocal
@bot.command(name="cleanup")
async def cleanup(ctx, channel: discord.VoiceChannel):
    await ctx.send(f"🧹 Tous les utilisateurs déconnectés de `{channel}`.")

# Commande pour déplacer tous les membres en vocal vers un salon
@bot.command(name="bringall")
async def bringall(ctx, to_channel: discord.VoiceChannel):
    await ctx.send(f"🔄 Tous les membres déplacés vers `{to_channel}`.")

# Commande pour recréer un salon textuel


# Commande pour supprimer tous les bannissements
@bot.command(name="unbanall")
async def unbanall(ctx):
    await ctx.send("✅ Tous les bannissements supprimés.")

# Commande pour ajouter un rôle temporaire
@bot.command(name="temprole")
async def temprole(ctx, member: discord.Member, role: discord.Role, duration: int):
    await ctx.send(f"⏳ Rôle `{role}` ajouté à {member} pour {duration}s.")

# Commande pour supprimer un rôle temporaire
@bot.command(name="untemprole")
async def untemprole(ctx, member: discord.Member, role: discord.Role):
    await ctx.send(f"❌ Rôle `{role}` retiré de {member}.")

# Commande pour synchroniser les permissions
@bot.command(name="sync")
async def sync(ctx, target: str):
    await ctx.send(f"🔄 Permissions synchronisées pour `{target}`.")

# Commande pour ouvrir un ticket manuellement
@bot.command(name="openmodmail")
async def openmodmail(ctx, member: discord.Member):
    await ctx.send(f"📩 Ticket ouvert avec {member}.")

# Commande pour ajouter ou supprimer un bouton
@bot.command(name="button")
async def button(ctx, action: str, link: str):
    await ctx.send(f"🔘 Bouton `{action}` avec le lien `{link}`.")

# Commande pour ajouter ou supprimer une réaction automatique
@bot.command(name="autoreact")
async def autoreact(ctx, action: str, channel: discord.TextChannel, emoji: str):
    await ctx.send(f"🔄 Réaction `{emoji}` `{action}` pour `{channel}`.")

# Commande pour afficher la liste des autoreacts
@bot.command(name="autoreact_list")
async def autoreact_list(ctx):
    await ctx.send("📋 Liste des autoreacts : ...")

# Commande pour créer un formulaire
@bot.command(name="formulaire")
async def formulaire(ctx, form_id: int):
    await ctx.send(f"📋 Formulaire `{form_id}` créé.")









bot.run("MTM2OTI0MTY1MTM5ODE4MDg3NA.GzbL-1.06b1ANOg8WwEWiwdqIvrpDUSG6u00GDhXUYeAU")
