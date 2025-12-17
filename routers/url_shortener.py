from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from oauth2.oauth2 import get_current_user
from models.models import LongUrls, Urls
from database import get_db
from utility.domain_extractor import extract_domain
from utility.base62_encoding import encode_base62
from schemas.schemas import (
    CreateLongURL,
    ShortURLResponse,
    URLCreateResponse,
)

router = APIRouter(prefix="/shorten", tags=["Urls"])


@router.post("/", response_model=URLCreateResponse)
async def create_short(
    long_url: CreateLongURL,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    url = await db.scalar(
        select(LongUrls).where(LongUrls.url == long_url.url)
    )
    if not url:
        new_long = LongUrls(
            owner_id=current_user.id, url=str(long_url.url)
        )
        try:
            db.add(new_long)
            await db.flush()
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{Exception}",
            )
    new_l = new_long if not url else url
    domain = extract_domain(new_l.url)
    result = await db.scalar(
        select(Urls).where(Urls.full_url_id == new_l.id)
    )
    if result:
        return URLCreateResponse(
            id=result.id,
            url_code=result.short_url,
            short_url=f"{domain}/{result.short_url}",
        )
    b62_encode = encode_base62(new_l.id + 10_000_000)
    new_short = Urls(
        owner_id=current_user.id,
        full_url_id=new_l.id,
        short_url=b62_encode,
    )
    short_link = f"{domain}/{b62_encode}"
    try:
        db.add(new_short)
        await db.commit()
        await db.refresh(new_short)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )
    return URLCreateResponse(
        id=new_short.id, url_code=b62_encode, short_url=short_link
    )


@router.get("/{code}", response_model=ShortURLResponse)
async def get_data_about_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.scalar(
        select(Urls)
        .options(selectinload(Urls.long))
        .where(Urls.short_url == code)
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such code doen't exists",
        )
    return ShortURLResponse(
        id=result.id, url=result.long.url, short_url=result.short_url
    )


@router.patch("/{code}", status_code=205)
async def update_short_url(
    url: CreateLongURL,
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.scalar(
        select(LongUrls)
        .join(LongUrls.short)
        .where(
            Urls.short_url == code,
            LongUrls.owner_id == current_user.id,
        )
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such code doesn't exist",
        )
    new_url = url.model_dump()
    for k, v in new_url.items():
        setattr(result, k, v)
    await db.commit()
    return Response(status_code=205)


@router.delete("/{code}", status_code=204)
async def delete_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.scalar(
        select(Urls)
        .join(Urls.long)
        .where(
            Urls.short_url == code,
            Urls.owner_id == current_user.id,
        )
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Such code doesn't exists",
        )
    try:
        await db.delete(result)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"{e}")
    return Response(status_code=204)
